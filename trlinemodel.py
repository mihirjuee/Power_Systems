import streamlit as st
import numpy as np
import schemdraw
import schemdraw.elements as elm

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Transmission Line Simulator", layout="centered")

st.title("⚡ Transmission Line Modeling & ABCD Analysis")

st.markdown("""
### Transmission Line Comparison
- Short Line Model
- Medium Line (π Model)
- Long Line (Distributed Model)

👉 Assumption: **Sending End Voltage is Fixed**
""")

# ================= SIDEBAR =================
st.sidebar.header("🔧 Line Parameters")

length = st.sidebar.slider("Line Length (km)", 10.0, 400.0, 150.0)

R_per_km = st.sidebar.number_input("Resistance R (Ω/km)", value=0.2)
X_per_km = st.sidebar.number_input("Reactance X (Ω/km)", value=0.4)
C_per_km = st.sidebar.number_input("Capacitance (μF/km)", value=0.006)

f = st.sidebar.slider("Frequency (Hz)", 40, 60, 50)

st.sidebar.header("⚡ Sending End Voltage")
Vs = st.sidebar.number_input("Vs (kV)", value=132.0)

st.sidebar.header("⚡ Load")
P = st.sidebar.number_input("Load Power (MW)", value=50.0)
pf = st.sidebar.slider("Power Factor", 0.5, 1.0, 0.8)
pf_type = st.sidebar.selectbox("PF Type", ["Lagging", "Leading"])

# ================= NETWORK PARAMETERS =================
Z = complex(R_per_km, X_per_km) * length
Y = 1j * 2 * np.pi * f * (C_per_km * 1e-6) * length

Vs_phase = Vs * 1e3 / np.sqrt(3)

Ir_mag = (P * 1e6) / (np.sqrt(3) * Vs * 1e3 * pf)
angle = np.arccos(pf)

if pf_type == "Lagging":
    Ir = Ir_mag * np.exp(-1j * angle)
else:
    Ir = Ir_mag * np.exp(1j * angle)

# ================= REGULATION =================
def regulation(Vs, Vr):
    return (abs(Vs) - abs(Vr)) / abs(Vr) * 100


# ================= CIRCUIT DIAGRAMS =================
def short_line_diagram():
    d = schemdraw.Drawing()

    d += elm.SourceSin().label("Vs")
    d += elm.Line().right()
    d += elm.Resistor().label("R")
    d += elm.Inductor().label("jX")
    d += elm.Line().right()

    d += elm.Resistor().label("Load (Vr)")  # FIXED

    return d


def medium_line_diagram():
    d = schemdraw.Drawing()

    d += elm.SourceSin().label("Vs")
    d += elm.Line().right()

    d.push()
    d += elm.Capacitor().down().label("Y/2")
    d += elm.Ground()
    d.pop()

    d += elm.Resistor().label("R")
    d += elm.Inductor().label("jX")

    d.push()
    d += elm.Capacitor().down().label("Y/2")
    d += elm.Ground()
    d.pop()

    d += elm.Line().right()

    d += elm.Resistor().label("Load (Vr)")  # FIXED

    return d


def long_line_diagram():
    d = schemdraw.Drawing()

    d += elm.SourceSin().label("Vs")

    for _ in range(3):
        d += elm.Resistor().label("RΔx")
        d += elm.Inductor().label("LΔx")

        d.push()
        d += elm.Capacitor().down().label("CΔx")
        d += elm.Ground()
        d.pop()

    d += elm.Line().right()

    d += elm.Resistor().label("Load (Vr)")  # FIXED

    return d


# ================= SIMULATION =================
if st.button("🚀 Run Simulation"):

    col1, col2, col3 = st.columns(3)

    # ================================================= SHORT LINE
    Vr_s = Vs_phase - Ir * Z
    Vr_s_kV = abs(Vr_s * np.sqrt(3)) / 1000
    reg_s = regulation(Vs_phase, Vr_s)

    with col1:
        st.markdown("### 🔹 Short Line")
        st.metric("Vr (kV)", f"{Vr_s_kV:.2f}")
        st.metric("Regulation (%)", f"{reg_s:.2f}")
        st.pyplot(short_line_diagram().draw().fig)

    # ================================================= MEDIUM LINE
    A_m = 1 + (Z * Y) / 2
    B_m = Z * (1 + (Z * Y) / 4)

    Ir_m = Ir + (Y / 2) * Vs_phase
    Vr_m = (Vs_phase - B_m * Ir_m) / A_m

    Vr_m_kV = abs(Vr_m * np.sqrt(3)) / 1000
    reg_m = regulation(Vs_phase, Vr_m)

    with col2:
        st.markdown("### 🔸 Medium Line (π Model)")
        st.metric("Vr (kV)", f"{Vr_m_kV:.2f}")
        st.metric("Regulation (%)", f"{reg_m:.2f}")
        st.pyplot(medium_line_diagram().draw().fig)

    # ================================================= LONG LINE
    gamma = np.sqrt(Z * Y + 0j)
    Zc = np.sqrt(Z / (Y + 1e-12))

    A_l = np.cosh(gamma)
    B_l = Zc * np.sinh(gamma)

    Vr_l = (Vs_phase - B_l * Ir) / A_l

    Vr_l_kV = abs(Vr_l * np.sqrt(3)) / 1000
    reg_l = regulation(Vs_phase, Vr_l)

    with col3:
        st.markdown("### 🔺 Long Line")
        st.metric("Vr (kV)", f"{Vr_l_kV:.2f}")
        st.metric("Regulation (%)", f"{reg_l:.2f}")
        st.pyplot(long_line_diagram().draw().fig)

    # ================= INTERPRETATION =================
    st.markdown("---")
    st.subheader("📘 Interpretation")

    st.write("""
🔹 Short Line → Neglects capacitance  
🔸 Medium Line → π model with shunt admittance  
🔺 Long Line → Distributed parameter model  

✔ As line length increases:
- Capacitance effect becomes significant  
- Voltage regulation changes  
- Long line model becomes necessary  
""")

    st.success("Simulation Completed Successfully ✅")

else:
    st.info("Click 'Run Simulation' to view results")
