# ============================================================
# FERRANTI EFFECT VIRTUAL LAB PRO
# Streamlit App
# ============================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Ferranti Effect Virtual Lab Pro", layout="wide")
st.title("⚡ Ferranti Effect Virtual Lab Pro")
st.markdown("### Understand why receiving-end voltage can exceed sending-end voltage at light/no load")

# ================= SIDEBAR =================
st.sidebar.header("🔧 Transmission Line Inputs")

Vs_kV = st.sidebar.number_input("Sending End Voltage (kV)", min_value=1.0, value=220.0)
freq = st.sidebar.number_input("Frequency (Hz)", min_value=1.0, value=50.0)
length = st.sidebar.number_input("Line Length (km)", min_value=1.0, value=300.0)

R_per_km = st.sidebar.number_input("Resistance R (Ω/km)", min_value=0.0, value=0.05)
L_per_km_mH = st.sidebar.number_input("Inductance L (mH/km)", min_value=0.0, value=1.0)
C_per_km_uF = st.sidebar.number_input("Capacitance C (µF/km)", min_value=0.0, value=0.01)

load_percent = st.sidebar.slider("Load Level (%)", 0, 100, 0)

model = st.sidebar.selectbox(
    "Transmission Line Model",
    ["Short Line", "Medium Line (Nominal π)", "Long Line"]
)

# ================= CALCULATIONS =================
w = 2 * np.pi * freq

# Total Parameters
R = R_per_km * length
L = (L_per_km_mH * 1e-3) * length
C = (C_per_km_uF * 1e-6) * length

Z = complex(R, w * L)
Y = complex(0, w * C)

Vs = Vs_kV * 1000

# Load current approximation
load_factor = load_percent / 100
I_load = load_factor * (Vs / abs(Z)) if abs(Z) > 0 else 0

# ABCD Constants
if model == "Short Line":
    A = 1
    B = Z

elif model == "Medium Line (Nominal π)":
    A = 1 + (Y * Z) / 2
    B = Z

else:  # Long Line Approximation
    gamma = np.sqrt(Y * Z)
    Zc = np.sqrt(Z / Y) if Y != 0 else Z
    A = np.cosh(gamma)
    B = Zc * np.sinh(gamma)

# Receiving End Voltage
Vr = Vs / abs(A + (B * I_load / Vs)) if Vs != 0 else 0

# Charging Current
Ic = abs(Vr * Y)

# Ferranti Effect
ferranti_rise = ((Vr - Vs) / Vs) * 100 if Vs != 0 else 0

# Voltage Regulation
voltage_reg = ((Vr - Vs) / Vs) * 100 if Vs != 0 else 0

# ================= DASHBOARD =================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Sending Voltage", f"{Vs/1000:.2f} kV")
col2.metric("Receiving Voltage", f"{Vr/1000:.2f} kV")
col3.metric("Ferranti Rise", f"{ferranti_rise:.2f} %")
col4.metric("Charging Current", f"{Ic:.2f} A")

# ================= EXPLANATION =================
st.subheader("📘 Ferranti Effect Explanation")

if ferranti_rise > 0:
    st.success(
        "At light/no load, line capacitance supplies charging current, causing receiving-end voltage to rise above sending-end voltage."
    )
else:
    st.info(
        "Ferranti effect is minimal under current operating conditions."
    )

# ================= VOLTAGE PROFILE =================
st.subheader("📈 Voltage Profile Along Transmission Line")

distance = np.linspace(0, length, 200)

# Simplified voltage rise profile
Vr_profile = Vs + (Vr - Vs) * (distance / length) ** 1.5

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(distance, Vr_profile / 1000, linewidth=3)
ax.set_xlabel("Distance Along Line (km)")
ax.set_ylabel("Voltage (kV)")
ax.set_title("Voltage Rise from Sending End to Receiving End")
ax.grid(True)

st.pyplot(fig)

# ================= VR vs LOAD =================
st.subheader("📊 Receiving Voltage vs Load")

loads = np.linspace(0, 100, 50)
Vr_loads = []

for lp in loads:
    lf = lp / 100
    I_temp = lf * (Vs / abs(Z)) if abs(Z) > 0 else 0
    Vr_temp = Vs / abs(A + (B * I_temp / Vs)) if Vs != 0 else 0
    Vr_loads.append(Vr_temp / 1000)

fig2, ax2 = plt.subplots(figsize=(10, 5))
ax2.plot(loads, Vr_loads, linewidth=3)
ax2.set_xlabel("Load (%)")
ax2.set_ylabel("Receiving Voltage (kV)")
ax2.set_title("Receiving-End Voltage vs Load")
ax2.grid(True)

st.pyplot(fig2)

# ================= KEY FORMULAS =================
st.subheader("🧮 Key Concepts")

st.latex(r"Ferranti\ Effect:\ V_R > V_S\ at\ light/no\ load")
st.latex(r"\%Voltage\ Regulation = \frac{V_R - V_S}{V_S}\times100")
st.latex(r"I_C = V_R \omega C")

# ================= VIRAL QUESTIONS =================
st.subheader("🔥 Engineering Challenge")

st.markdown("""
### Why is Ferranti Effect more severe in:
- Long transmission lines?
- Underground cables?
- Higher voltages?
""")

# ================= FOOTER =================
st.markdown("---")
st.caption("Designed for Electrical Engineering Students | Power System Visualization Tool")
