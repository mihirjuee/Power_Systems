import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Symmetrical Fault Transient", layout="wide")

st.title("⚡ Symmetrical Fault Transient Analysis")

# ================= SIDEBAR INPUT =================
st.sidebar.header("🔧 Input Parameters")

V = st.sidebar.number_input("Source Voltage (V)", value=230.0)
R = st.sidebar.number_input("Resistance (Ω)", value=1.0)
L = st.sidebar.number_input("Inductance (H)", value=0.05)
f = st.sidebar.number_input("Frequency (Hz)", value=50.0)
theta_deg = st.sidebar.slider("Fault Inception Angle (°)", 0, 180, 0)

# ================= CALCULATIONS =================
omega = 2 * np.pi * f
theta = np.radians(theta_deg)
tau = L / R

t = np.linspace(0, 0.1, 1000)

# Peak current
Im = V / np.sqrt(R**2 + (omega*L)**2)

# DC offset (depends on fault angle)
Idc = Im * np.sin(theta)

# Total current
i_ac = Im * np.sin(omega*t + theta)
i_dc = Idc * np.exp(-t / tau)
i_total = i_ac + i_dc

# ================= PLOT =================
st.subheader("📈 Fault Current Waveform")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(t, i_total, label="Total Current")
ax.plot(t, i_ac, linestyle='--', label="AC Component")
ax.plot(t, i_dc, linestyle=':', label="DC Offset")

ax.set_xlabel("Time (s)")
ax.set_ylabel("Current (A)")
ax.legend()
ax.grid()

st.pyplot(fig)

# ================= METRICS =================
col1, col2, col3 = st.columns(3)
col1.metric("Time Constant τ (s)", f"{tau:.4f}")
col2.metric("Peak AC Current (A)", f"{Im:.2f}")
col3.metric("Initial DC Offset", f"{Idc:.2f}")

# ================= CIRCUIT DIAGRAM =================
st.subheader("🔌 Circuit Diagram")

d = schemdraw.Drawing()

# Source
d += elm.SourceSin().label("V")

# Line
d += elm.Line().right()

# Resistance
d += elm.Resistor().label(f"R = {R}Ω")

# Inductance
d += elm.Inductor().label(f"L = {L}H")

# Fault switch
d += elm.Switch().down().label("Fault")

# Ground
d += elm.Ground()

# Return path
d += elm.Line().left()

st.pyplot(d.draw())
