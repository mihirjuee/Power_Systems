import streamlit as st
import numpy as np
import schemdraw
import schemdraw.elements as elm

# ================= PAGE =================
st.set_page_config(page_title="Transmission Line Case 1", layout="centered")

st.title("⚡ Transmission Line Analysis (Case 1: Vs Fixed)")

st.markdown("""
### 🔹 Sending End Voltage Fixed (Vs)
Used for:
- Voltage regulation
- Line performance
- Loss analysis
""")

# ================= INPUTS =================
st.sidebar.header("🔧 Line Parameters")

length = st.sidebar.slider("Line Length (km)", 10.0, 400.0, 150.0)

R = st.sidebar.number_input("Resistance (Ω/km)", value=0.2)
X = st.sidebar.number_input("Reactance (Ω/km)", value=0.4)
C = st.sidebar.number_input("Capacitance (μF/km)", value=0.006)

f = st.sidebar.slider("Frequency (Hz)", 40, 60, 50)

st.sidebar.header("⚡ Sending End Voltage")
Vs = st.sidebar.number_input("Vs (kV)", value=132.0)

st.sidebar.header("⚡ Load")
P = st.sidebar.number_input("Load Power (MW)", value=50.0)
pf = st.sidebar.slider("Power Factor", 0.5, 1.0, 0.8)
pf_type = st.sidebar.selectbox("PF Type", ["Lagging", "Leading"])

# ================= NETWORK =================
Z = complex(R, X) * length
Y = 1j * 2 * np.pi * f * (C * 1e-6) * length

Vs_phase = Vs * 1e3 / np.sqrt(3)

Ir_mag = (P * 1e6) / (np.sqrt(3) * Vs * 1e3 * pf)
angle = np.arccos(pf)

Ir = Ir_mag * np.exp(-1j * angle if pf_type == "Lagging" else 1j * angle)

def regulation(Vs, Vr):
    return (abs(Vs) - abs(Vr)) / abs(Vr) * 100


# ================= CIRCUIT DIAGRAMS =================

# 🔹 SHORT LINE
def short_line_circuit():
    d = schemdraw.Drawing()

    d += elm.SourceSin().label("Vs")
    d += elm.Line().right()
    d += elm.Resistor().label("R")
    d += elm.Inductor().label("jX")
    d += elm.Line().right()
    #d += elm.Dot()
    d += elm.Line().down(1)
    d += elm.Resistor().label("Load")
    d += elm.Line().left(12)
    d += elm.Line().up(1)
    d += elm.Label().at((2, -2)).label("Short Transmission Line Model")
    return d


# 🔸 MEDIUM LINE (π model)
def medium_line_circuit():
    d = schemdraw.Drawing()

    d += elm.SourceSin().label("Vs")
    d += elm.Line().right()

    # shunt at sending end
    d.push()
    d += elm.Capacitor().down().label("Y/2")
    #d += elm.Ground()
    d.pop()

    d += elm.Resistor().label("R")
    d += elm.Inductor().label("jX")

    # shunt at receiving end
    d.push()
    d += elm.Capacitor().down().label("Y/2")
    #d += elm.Ground()
    d.pop()

    d += elm.Line().right()
    #d += elm.Dot()
    d += elm.Line().down(0.06)
    d += elm.Resistor().label("Load")
    d += elm.Line().left(12)
    d += elm.Label().at((6, -2)).label("Medium Transmission Line Model")
    return d


# 🔺 LONG LINE
def long_line_circuit():
    d = schemdraw.Drawing()

    d += elm.SourceSin().label("Vs")

    for _ in range(3):
        # Series impedance
        d += elm.Resistor().right().label("RΔx")
        d += elm.Inductor().right().label("LΔx")

        # Shunt capacitance
        d.push()
        d += elm.Capacitor().down().label("CΔx")
        #d += elm.Ground()
        d.pop()

        # spacing between sections
        d += elm.Line().right()

    # Load
    d += elm.Line().right().linestyle("--")
    d += elm.Line().down(0.1)
    d += elm.Resistor().label("Load (Vr)")
    d += elm.Line().left().linestyle("--")
    d += elm.Line().left(26)
    return d


# ================= CALC =================
def short_vr():
    return Vs_phase - Ir * Z

def medium_vr():
    A = 1 + (Z * Y) / 2
    B = Z * (1 + (Z * Y) / 4)
    Ir_m = Ir + (Y / 2) * Vs_phase
    return (Vs_phase - B * Ir_m) / A

def long_vr():
    gamma = np.sqrt(Z * Y + 0j)
    Zc = np.sqrt(Z / (Y + 1e-12))
    A = np.cosh(gamma)
    B = Zc * np.sinh(gamma)
    return (Vs_phase - B * Ir) / A


# ================= RUN =================
if st.button("🚀 Run Analysis"):

    col1, col2 = st.columns(2)

    # SHORT
    Vr_s = short_vr()
    reg_s = regulation(Vs_phase, Vr_s)

    with col1:
        st.markdown("### 🔹 Short Line")
        st.metric("Vr (kV)", f"{abs(Vr_s*np.sqrt(3))/1000:.2f}")
        st.metric("Regulation (%)", f"{reg_s:.2f}")
        st.pyplot(short_line_circuit().draw().fig)

    # MEDIUM
    Vr_m = medium_vr()
    reg_m = regulation(Vs_phase, Vr_m)

    with col2:
        st.markdown("### 🔸 Medium (π)")
        st.metric("Vr (kV)", f"{abs(Vr_m*np.sqrt(3))/1000:.2f}")
        st.metric("Regulation (%)", f"{reg_m:.2f}")
        st.pyplot(medium_line_circuit().draw().fig)

    # ================= LONG LINE (FULL WIDTH BELOW) =================
    st.markdown("---")
    st.subheader("🔺 Long Transmission Line (Distributed Model)")

    Vr_l = long_vr()
    reg_l = regulation(Vs_phase, Vr_l)

    colA, colB = st.columns([1, 2])

    with colA:
        st.metric("Vr (kV)", f"{abs(Vr_l*np.sqrt(3))/1000:.2f}")
        st.metric("Regulation (%)", f"{reg_l:.2f}")

    with colB:
        st.pyplot(long_line_circuit().draw().fig)

    # ================= INTERPRETATION =================
    st.markdown("---")
    st.subheader("📘 Interpretation")

    st.write("""
✔ Short line → only series impedance  
✔ Medium line → π model with shunt capacitance  
✔ Long line → distributed parameters  

👉 As length increases:
- Voltage drop increases  
- Charging current increases  
- Long line shows Ferranti effect at light load
""")

    st.success("Analysis Completed ✅")

else:
    st.info("Click 'Above'")
