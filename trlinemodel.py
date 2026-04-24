import streamlit as st
import numpy as np

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Transmission Line Comparison", layout="centered")

st.title("⚡ Transmission Line Modeling Comparison (ABCD Based)")
import schemdraw
import schemdraw.elements as elm
import matplotlib.pyplot as plt

st.subheader("📐 Transmission Line Models")

tab1, tab2, tab3 = st.tabs(["Short Line", "Medium (π)", "Long Line"])

# ================= SHORT LINE =================
with tab1:
    st.markdown("### 🔹 Short Transmission Line Model")

    d = schemdraw.Drawing()

    d += elm.SourceSin().label("Vs")
    d += elm.Line().right()
    d += elm.Resistor().label("R")
    d += elm.Inductor().label("jX")
    d += elm.Line().right()
    d += elm.Load().label("Load (Vr)")

    fig = d.draw()
    st.pyplot(fig)


# ================= MEDIUM LINE (PI MODEL) =================
with tab2:
    st.markdown("### 🔸 Medium Transmission Line (π Model)")

    d = schemdraw.Drawing()

    d += elm.SourceSin().label("Vs")
    d += elm.Line().right()

    # Shunt capacitance (sending end)
    d.push()
    d += elm.Capacitor().down().label("Y/2")
    d += elm.Ground()
    d.pop()

    # Series impedance
    d += elm.Resistor().label("R")
    d += elm.Inductor().label("jX")

    # Shunt capacitance (receiving end)
    d.push()
    d += elm.Capacitor().down().label("Y/2")
    d += elm.Ground()
    d.pop()

    d += elm.Line().right()
    d += elm.Load().label("Load (Vr)")

    fig = d.draw()
    st.pyplot(fig)


# ================= LONG LINE =================
with tab3:
    st.markdown("### 🔺 Long Transmission Line Model")

    st.write("""
This model uses **distributed parameters**:
- Resistance (R), Inductance (L)
- Capacitance (C), Conductance (G)

Instead of lumped elements, they are spread continuously along the line.
""")

    d = schemdraw.Drawing()

    d += elm.SourceSin().label("Vs")

    # Repeated sections (to show distributed nature)
    for _ in range(3):
        d += elm.Resistor().label("RΔx")
        d += elm.Inductor().label("LΔx")

        d.push()
        d += elm.Capacitor().down().label("CΔx")
        d += elm.Ground()
        d.pop()

    d += elm.Line().right()
    d += elm.Load().label("Vr")

    fig = d.draw()
    st.pyplot(fig)
st.markdown("""
### Compare Transmission Line Models
- Short Line (< 80 km)
- Medium Line (80–250 km, π model)
- Long Line (> 250 km, distributed model)

👉 **Assumption: Sending End Voltage is Fixed**
""")

# ================= SIDEBAR INPUTS =================
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
pf_type = st.sidebar.selectbox("Power Factor Type", ["Lagging", "Leading"])

# ================= NETWORK PARAMETERS =================
Z = complex(R_per_km, X_per_km) * length
Y = 1j * 2 * np.pi * f * (C_per_km * 1e-6) * length

Vs_phase = Vs * 1e3 / np.sqrt(3)

# Load current magnitude
Ir_mag = (P * 1e6) / (np.sqrt(3) * Vs * 1e3 * pf)
angle = np.arccos(pf)

if pf_type == "Lagging":
    Ir = Ir_mag * np.exp(-1j * angle)
else:
    Ir = Ir_mag * np.exp(1j * angle)

# ================= REGULATION FUNCTION =================
def regulation(Vs, Vr):
    return (abs(Vs) - abs(Vr)) / abs(Vr) * 100


# ================= MAIN BUTTON =================
if st.button("🚀 Compare Models"):

    st.subheader("📊 Results")

    col1, col2, col3 = st.columns(3)

    # =========================================================
    # 🔹 SHORT LINE MODEL
    # =========================================================
    A_s = 1
    B_s = Z

    Vr_s = Vs_phase - Ir * Z

    Vr_s_kV = abs(Vr_s * np.sqrt(3)) / 1000
    reg_s = regulation(Vs_phase, Vr_s)

    with col1:
        st.markdown("### 🔹 Short Line")
        st.metric("Receiving Voltage (kV)", f"{Vr_s_kV:.2f}")
        st.metric("Regulation (%)", f"{reg_s:.2f}")

        st.markdown("**ABCD Matrix**")
        st.latex(r"""
        \begin{bmatrix}
        1 & Z \\
        0 & 1
        \end{bmatrix}
        """)

    # =========================================================
    # 🔸 MEDIUM LINE (π MODEL)
    # =========================================================
    A_m = 1 + (Z * Y) / 2
    B_m = Z * (1 + (Z * Y) / 4)
    C_m = Y * (1 + (Z * Y) / 4)
    D_m = A_m

    Ir_m = Ir + (Y / 2) * Vs_phase
    Vr_m = (Vs_phase - B_m * Ir_m) / A_m

    Vr_m_kV = abs(Vr_m * np.sqrt(3)) / 1000
    reg_m = regulation(Vs_phase, Vr_m)

    with col2:
        st.markdown("### 🔸 Medium Line (π Model)")
        st.metric("Receiving Voltage (kV)", f"{Vr_m_kV:.2f}")
        st.metric("Regulation (%)", f"{reg_m:.2f}")

        st.markdown("**ABCD Matrix**")
        st.latex(r"""
        \begin{bmatrix}
        A & B \\
        C & D
        \end{bmatrix}
        =
        \begin{bmatrix}
        1+\frac{ZY}{2} & Z\left(1+\frac{ZY}{4}\right) \\
        Y\left(1+\frac{ZY}{4}\right) & 1+\frac{ZY}{2}
        \end{bmatrix}
        """)

    # =========================================================
    # 🔺 LONG LINE MODEL
    # =========================================================
    gamma = np.sqrt(Z * Y + 0j)
    Zc = np.sqrt(Z / (Y + 1e-12))

    A_l = np.cosh(gamma)
    B_l = Zc * np.sinh(gamma)
    C_l = (1 / Zc) * np.sinh(gamma)
    D_l = A_l

    Vr_l = (Vs_phase - B_l * Ir) / A_l

    Vr_l_kV = abs(Vr_l * np.sqrt(3)) / 1000
    reg_l = regulation(Vs_phase, Vr_l)

    with col3:
        st.markdown("### 🔺 Long Line")
        st.metric("Receiving Voltage (kV)", f"{Vr_l_kV:.2f}")
        st.metric("Regulation (%)", f"{reg_l:.2f}")

        st.markdown("**ABCD Matrix**")
        st.latex(r"""
        \begin{bmatrix}
        \cosh(\gamma) & Z_c\sinh(\gamma) \\
        \frac{1}{Z_c}\sinh(\gamma) & \cosh(\gamma)
        \end{bmatrix}
        """)

    # =========================================================
    # 📘 INTERPRETATION
    # =========================================================
    st.markdown("---")
    st.subheader("📘 Interpretation")

    st.write("""
🔹 **Short Line**
- No capacitance effect
- Accurate only for short distances

🔸 **Medium Line**
- π model includes shunt capacitance
- More realistic for 80–250 km

🔺 **Long Line**
- Distributed parameter model
- Most accurate representation
- Shows Ferranti effect at light load

👉 As line length increases, capacitance effects dominate.
""")

    st.success("✅ Simulation Completed Successfully")
else:
    st.info("Click 'Compare Models' to run analysis")
