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

V_rms = st.sidebar.number_input("Source Voltage (Vrms)", value=230.0)
R = st.sidebar.number_input("Resistance (Ω)", value=1.0)
L = st.sidebar.number_input("Inductance (H)", value=0.05)
f = st.sidebar.number_input("Frequency (Hz)", value=50.0)
theta_deg = st.sidebar.slider("Fault Inception Angle (°)", 0, 180, 0)

# ================= CALCULATIONS =================
omega = 2 * np.pi * f
theta = np.radians(theta_deg)
tau = L / R
V_m = V_rms * np.sqrt(2)
Z = np.sqrt(R**2 + (omega * L)**2)
phi = np.arctan((omega * L) / R)
Im = V_m / Z

# Time vector: Plot up to 5 time constants to show decay
t = np.linspace(0, 5 * tau, 1000)

# Total current equation: i(t) = Im*sin(wt + theta - phi) + [Im*sin(phi - theta)]*e^(-t/tau)
i_ac = Im * np.sin(omega * t + theta - phi)
i_dc = (Im * np.sin(phi - theta)) * np.exp(-t / tau)
i_total = i_ac + i_dc

# ================= PLOT =================
st.subheader("📈 Fault Current Waveform")

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(t, i_total, label="Total Fault Current", color='black', linewidth=1.5)
ax.plot(t, i_ac, linestyle='--', label="AC Steady-State Component", color='blue', alpha=0.6)
ax.plot(t, i_dc, linestyle=':', label="DC Offset", color='red')

ax.set_xlabel("Time (s)")
ax.set_ylabel("Current (A)")
ax.axhline(0, color='gray', linewidth=0.5)
ax.legend()
ax.grid(True, linestyle='--', alpha=0.7)

st.pyplot(fig)

# ================= METRICS =================
col1, col2, col3 = st.columns(3)
col1.metric("Time Constant τ (s)", f"{tau:.4f}")
col2.metric("Peak AC Current (A)", f"{Im:.2f}")
col3.metric("Initial DC Offset (A)", f"{i_dc[0]:.2f}")

# ================= CIRCUIT DIAGRAM =================
import io
from PIL import Image
st.subheader("🔌 Circuit Schematic")

d = schemdraw.Drawing(show=False)

d += (V1 := elm.SourceSin().label("Source", loc="left"))
d += elm.Resistor().right().label(f"{R}Ω")
d += elm.Inductor().right().label(f"{L}H")


# Return path
d += elm.Line().left().tox(V1.start)
d += elm.Line().up().to(V1.start)

# ---- SAFE RENDER ----
img = d.draw()

buf = io.BytesIO()
buf.write(img.get_imagedata('png'))
buf.seek(0)

st.image(buf, use_container_width=True)
