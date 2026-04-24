import streamlit as st
import numpy as np

st.set_page_config(page_title="Transmission Line Comparison", layout="centered")

st.title("⚡ Transmission Line Modeling Comparison")

st.markdown("""
Compare:
- Short Line (< 80 km)
- Medium Line (80–250 km, π model)
- Long Line (> 250 km, distributed)
""")

# --- INPUTS ---
st.sidebar.header("🔧 Line Parameters")

length = st.sidebar.slider("Line Length (km)", 10.0, 400.0, 150.0)

R_per_km = st.sidebar.number_input("Resistance R (Ω/km)", value=0.2)
X_per_km = st.sidebar.number_input("Reactance X (Ω/km)", value=0.4)
C_per_km = st.sidebar.number_input("Capacitance (μF/km)", value=0.01)

f = st.sidebar.slider("Frequency (Hz)", 40, 60, 50)

st.sidebar.header("⚡ Load")

Vr = st.sidebar.number_input("Receiving Voltage (kV)", value=132.0)
P = st.sidebar.number_input("Load Power (MW)", value=50.0)
pf = st.sidebar.slider("Power Factor", 0.5, 1.0, 0.8)
pf_type = st.sidebar.selectbox("PF Type", ["Lagging", "Leading"])

# --- COMMON CALCULATIONS ---
Z = complex(R_per_km, X_per_km) * length
Y = 1j * 2 * np.pi * f * (C_per_km * 1e-6) * length

Vr_phase = Vr * 1e3 / np.sqrt(3)

Ir_mag = (P * 1e6) / (np.sqrt(3) * Vr * 1e3 * pf)
angle = np.arccos(pf)

if pf_type == "Lagging":
    Ir = Ir_mag * np.exp(-1j * angle)
else:
    Ir = Ir_mag * np.exp(1j * angle)

# --- BUTTON ---
if st.button("🚀 Compare Models"):

    st.subheader("📊 Results")

    col1, col2, col3 = st.columns(3)

    # ================= SHORT LINE =================
    Vs_short = Vr_phase + Ir * Z
    Vs_short_kV = abs(Vs_short) * np.sqrt(3) / 1000
    reg_short = (Vs_short_kV - Vr) / Vr * 100

    with col1:
        st.markdown("### 🔹 Short Line")
        st.metric("Vs (kV)", f"{Vs_short_kV:.2f}")
        st.metric("Regulation (%)", f"{reg_short:.2f}")

    # ================= MEDIUM LINE (PI MODEL) =================
    Y_half = Y / 2

    Ir1 = Ir + Vr_phase * Y_half
    Vs_medium = Vr_phase + Ir1 * Z
    Is = Ir1 + Vs_medium * Y_half

    Vs_medium_kV = abs(Vs_medium) * np.sqrt(3) / 1000
    reg_medium = (Vs_medium_kV - Vr) / Vr * 100

    with col2:
        st.markdown("### 🔸 Medium (π Model)")
        st.metric("Vs (kV)", f"{Vs_medium_kV:.2f}")
        st.metric("Regulation (%)", f"{reg_medium:.2f}")

    # ================= LONG LINE =================
    gamma = np.sqrt(Z * Y)
    Zc = np.sqrt(Z / Y)

    A = np.cosh(gamma)
    B = Zc * np.sinh(gamma)

    Vs_long = A * Vr_phase + B * Ir

    Vs_long_kV = abs(Vs_long) * np.sqrt(3) / 1000
    reg_long = (Vs_long_kV - Vr) / Vr * 100

    with col3:
        st.markdown("### 🔺 Long Line")
        st.metric("Vs (kV)", f"{Vs_long_kV:.2f}")
        st.metric("Regulation (%)", f"{reg_long:.2f}")

    st.markdown("---")

    # --- INTERPRETATION ---
    st.subheader("📘 Interpretation")

    st.write("""
🔹 Short Line:
- Ignores capacitance → less accurate for long distances

🔸 Medium Line:
- Includes capacitance using π model
- More realistic

🔺 Long Line:
- Uses distributed parameters
- Most accurate for long distances

👉 Notice how results diverge as line length increases.
""")

    st.success("✅ Comparison Complete")

else:
    st.info("Click 'Compare Models'")
