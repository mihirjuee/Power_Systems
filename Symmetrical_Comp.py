import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Symmetrical Components Lab", layout="wide")

st.title("⚡ Symmetrical Components & Vector Visualization Lab")

# ---------------- INPUT ----------------
st.sidebar.header("Phase Voltages")

def phasor(mag, angle_deg):
    return mag * np.exp(1j * np.deg2rad(angle_deg))

# -------- Va --------
st.sidebar.subheader("Va")
Va_mag = st.sidebar.number_input("Magnitude Va", value=230.0, step=1.0)
Va_ang = st.sidebar.number_input("Angle Va (deg)", value=0.0, step=1.0)

# -------- Vb --------
st.sidebar.subheader("Vb")
Vb_mag = st.sidebar.number_input("Magnitude Vb", value=230.0, step=1.0)
Vb_ang = st.sidebar.number_input("Angle Vb (deg)", value=-120.0, step=1.0)

# -------- Vc --------
st.sidebar.subheader("Vc")
Vc_mag = st.sidebar.number_input("Magnitude Vc", value=230.0, step=1.0)
Vc_ang = st.sidebar.number_input("Angle Vc (deg)", value=120.0, step=1.0)

# Convert to phasors
Va = phasor(Va_mag, Va_ang)
Vb = phasor(Vb_mag, Vb_ang)
Vc = phasor(Vc_mag, Vc_ang)

# ---------------- SYMMETRICAL COMPONENTS ----------------
a = np.exp(1j * 2 * np.pi / 3)

V0 = (Va + Vb + Vc) / 3
V1 = (Va + a * Vb + a**2 * Vc) / 3
V2 = (Va + a**2 * Vb + a * Vc) / 3

# ---------------- DISPLAY VALUES ----------------
st.subheader("📊 Sequence Components")

colA, colB, colC = st.columns(3)
colA.metric("V0 (Zero)", f"{abs(V0):.2f} ∠ {np.angle(V0, deg=True):.1f}°")
colB.metric("V1 (Positive)", f"{abs(V1):.2f} ∠ {np.angle(V1, deg=True):.1f}°")
colC.metric("V2 (Negative)", f"{abs(V2):.2f} ∠ {np.angle(V2, deg=True):.1f}°")

# ---------------- VECTOR DRAW FUNCTION ----------------
def draw_vector(ax, start, end, color, label):
    arrow = FancyArrowPatch(
        posA=(start.real, start.imag),
        posB=(end.real, end.imag),
        arrowstyle='->',
        mutation_scale=15,
        linewidth=2,
        color=color
    )
    ax.add_patch(arrow)
    ax.text(end.real, end.imag, label, color=color)

def setup_axis(ax, title):
    ax.set_title(title)
    ax.axhline(0)
    ax.axvline(0)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.set_xlim(-300, 300)
    ax.set_ylim(-300, 300)

# ---------------- ORIGINAL PHASORS ----------------
st.subheader("📉 Original Phase Phasors")

fig0, ax0 = plt.subplots()
draw_vector(ax0, 0+0j, Va, "red", "Va")
draw_vector(ax0, 0+0j, Vb, "green", "Vb")
draw_vector(ax0, 0+0j, Vc, "blue", "Vc")
setup_axis(ax0, "Original System")
st.pyplot(fig0)

# ---------------- SEQUENCE PHASORS ----------------
st.subheader("🔁 Symmetrical Component Phasors")

col1, col2, col3 = st.columns(3)

# Positive
with col1:
    fig1, ax1 = plt.subplots()
    draw_vector(ax1, 0, V1, "blue", "Va1")
    draw_vector(ax1, 0, V1*a**2, "blue", "Vb1")
    draw_vector(ax1, 0, V1*a, "blue", "Vc1")
    setup_axis(ax1, "Positive (ABC)")
    st.pyplot(fig1)

# Negative
with col2:
    fig2, ax2 = plt.subplots()
    draw_vector(ax2, 0, V2, "orange", "Va2")
    draw_vector(ax2, 0, V2*a, "orange", "Vb2")
    draw_vector(ax2, 0, V2*a**2, "orange", "Vc2")
    setup_axis(ax2, "Negative (ACB)")
    st.pyplot(fig2)

# Zero
with col3:
    fig3, ax3 = plt.subplots()
    draw_vector(ax3, 0, V0, "purple", "Va0")
    draw_vector(ax3, 0, V0, "purple", "Vb0")
    draw_vector(ax3, 0, V0, "purple", "Vc0")
    setup_axis(ax3, "Zero (In-phase)")
    st.pyplot(fig3)

# ---------------- RECONSTRUCTION ----------------
st.subheader("🔁 Vector Reconstruction")

figR, axes = plt.subplots(1, 3, figsize=(15, 4))

# ---------------- GLOBAL AXIS CALCULATION ----------------
vectors_all = [
    V1, V1+V2, V1+V2+V0,                         # Va
    a**2*V1, a**2*V1 + a*V2, a**2*V1 + a*V2 + V0,  # Vb
    a*V1, a*V1 + a**2*V2, a*V1 + a**2*V2 + V0      # Vc
]

max_val = max(abs(v) for v in vectors_all)
if max_val < 1e-6:
    max_val = 1

GLOBAL_LIMIT = max_val * 1.3


# ---------------- RECONSTRUCTION FUNCTION ----------------
#st.subheader("🔁 Vector Reconstruction (Combined Plot)")

fig, ax = plt.subplots(figsize=(7, 7))

origin = 0 + 0j

# ---------------- PREPARE ALL PHASES ----------------
phases = {
    "Va": (V1, V2, V0),
    "Vb": (a**2 * V1, a * V2, V0),
    "Vc": (a * V1, a**2 * V2, V0)
}

# Colors for each phase resultant
result_colors = {
    "Va": "red",
    "Vb": "green",
    "Vc": "blue"
}

# ---------------- DRAW ALL ----------------
all_vectors = []

for name, (V1p, V2p, V0p) in phases.items():

    end1 = V1p
    end2 = V1p + V2p
    final = V1p + V2p + V0p

    # Collect for scaling
    all_vectors.extend([end1, end2, final])

    # Draw sequence vectors (same colors)
    draw_vector(ax, origin, end1, "blue", f"{name}1")
    draw_vector(ax, end1, end2, "orange", f"{name}2")
    draw_vector(ax, end2, final, "purple", f"{name}0")

    # Draw resultant
    draw_vector(ax, origin, final, result_colors[name], name)

# ---------------- AUTO AXIS ----------------
max_val = max(abs(v) for v in all_vectors)
if max_val < 1e-6:
    max_val = 1

limit = max_val * 1.4

ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)

# ---------------- STYLE ----------------
ax.set_title("Combined Vector Reconstruction (Va, Vb, Vc)")
ax.axhline(0)
ax.axvline(0)
ax.set_aspect('equal')
ax.grid(True)

st.pyplot(fig)

# ---------------- EXPLANATION OF a ----------------
st.subheader("📘 What is 'a'?")

st.latex(r"a = e^{j\frac{2\pi}{3}} = 1\angle 120^\circ")

st.markdown("""
### ⚡ Meaning
- 'a' rotates a vector by **120° anticlockwise**

### 🔁 Properties
- a² = 1∠240° = -120°
- a³ = 1
- 1 + a + a² = 0

### ⚡ Usage
- Generates balanced 3-phase sets
- Used in symmetrical component transformation
""")

# ---------------- LEGEND ----------------
st.markdown("""
### 🎨 Color Legend
- 🔵 Positive Sequence (V1)
- 🟠 Negative Sequence (V2)
- 🟣 Zero Sequence (V0)
- 🔴 Resultant Phase
""")
