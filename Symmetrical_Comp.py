import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Symmetrical Components Lab", layout="wide")

st.title("⚡ Symmetrical Components & Vector Visualization Lab")

st.markdown("""
Visualize:
- Original 3-phase system  
- Symmetrical components (V₀, V₁, V₂)  
- Vector reconstruction of Va, Vb, Vc  
""")

# ---------------- INPUT ----------------
st.sidebar.header("Phase Voltages")

def phasor(mag, angle_deg):
    return mag * np.exp(1j * np.deg2rad(angle_deg))

Va_mag = st.sidebar.slider("Va Magnitude", 0.0, 500.0, 230.0)
Va_ang = st.sidebar.slider("Va Angle (deg)", -180, 180, 0)

Vb_mag = st.sidebar.slider("Vb Magnitude", 0.0, 500.0, 230.0)
Vb_ang = st.sidebar.slider("Vb Angle (deg)", -180, 180, -120)

Vc_mag = st.sidebar.slider("Vc Magnitude", 0.0, 500.0, 230.0)
Vc_ang = st.sidebar.slider("Vc Angle (deg)", -180, 180, 120)

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

colA.metric("V0 (Zero Seq)", f"{abs(V0):.2f} ∠ {np.angle(V0, deg=True):.1f}°")
colB.metric("V1 (Positive Seq)", f"{abs(V1):.2f} ∠ {np.angle(V1, deg=True):.1f}°")
colC.metric("V2 (Negative Seq)", f"{abs(V2):.2f} ∠ {np.angle(V2, deg=True):.1f}°")

# ---------------- PHASOR FUNCTION ----------------
def draw_phasors(ax, phasors, labels, title):
    for ph, label in zip(phasors, labels):
        ax.arrow(0, 0, ph.real, ph.imag, length_includes_head=True)
        ax.text(ph.real, ph.imag, label)

    ax.set_title(title)
    ax.axhline(0)
    ax.axvline(0)
    ax.set_aspect('equal')
    ax.grid(True)

# ---------------- ORIGINAL PHASORS ----------------
st.subheader("📉 Original Phase Phasors")

fig0, ax0 = plt.subplots()
draw_phasors(ax0, [Va, Vb, Vc], ["Va", "Vb", "Vc"], "Original System")
st.pyplot(fig0)

# ---------------- SEQUENCE PHASORS ----------------
st.subheader("🔁 Symmetrical Component Phasors")

col1, col2, col3 = st.columns(3)

# Positive
with col1:
    Va1 = V1
    Vb1 = V1 * a**2
    Vc1 = V1 * a

    fig1, ax1 = plt.subplots()
    draw_phasors(ax1, [Va1, Vb1, Vc1], ["Va1", "Vb1", "Vc1"], "Positive (ABC)")
    st.pyplot(fig1)

# Negative
with col2:
    Va2 = V2
    Vb2 = V2 * a
    Vc2 = V2 * a**2

    fig2, ax2 = plt.subplots()
    draw_phasors(ax2, [Va2, Vb2, Vc2], ["Va2", "Vb2", "Vc2"], "Negative (ACB)")
    st.pyplot(fig2)

# Zero
with col3:
    Va0 = V0
    Vb0 = V0
    Vc0 = V0

    fig3, ax3 = plt.subplots()
    draw_phasors(ax3, [Va0, Vb0, Vc0], ["Va0", "Vb0", "Vc0"], "Zero (In-phase)")
    st.pyplot(fig3)

# ---------------- RECONSTRUCTION ----------------
st.subheader("🔁 Vector Reconstruction (Va, Vb, Vc)")

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

def draw_reconstruction(ax, V1, V2, V0, title):
    # V1
    ax.arrow(0, 0, V1.real, V1.imag, length_includes_head=True)
    ax.text(V1.real, V1.imag, "V1")

    # V2
    end1 = V1
    ax.arrow(end1.real, end1.imag, V2.real, V2.imag, length_includes_head=True)
    ax.text(end1.real + V2.real, end1.imag + V2.imag, "V2")

    # V0
    end2 = V1 + V2
    ax.arrow(end2.real, end2.imag, V0.real, V0.imag, length_includes_head=True)
    ax.text(end2.real + V0.real, end2.imag + V0.imag, "V0")

    # Resultant
    V_final = V1 + V2 + V0
    ax.arrow(0, 0, V_final.real, V_final.imag, linestyle="--")
    ax.text(V_final.real, V_final.imag, title, color="red")

    ax.set_title(title)
    ax.axhline(0)
    ax.axvline(0)
    ax.set_aspect('equal')
    ax.grid(True)

# Va
draw_reconstruction(axes[0], V1, V2, V0, "Va")

# Vb
V1b = a**2 * V1
V2b = a * V2
draw_reconstruction(axes[1], V1b, V2b, V0, "Vb")

# Vc
V1c = a * V1
V2c = a**2 * V2
draw_reconstruction(axes[2], V1c, V2c, V0, "Vc")

st.pyplot(fig)

# ---------------- THEORY ----------------
st.subheader("📘 Key Concepts")

st.markdown("""
### ⚡ Symmetrical Components:
- **Positive Sequence (V1)** → Balanced ABC system  
- **Negative Sequence (V2)** → Reverse rotation (ACB)  
- **Zero Sequence (V0)** → All in phase  

### ⚡ Reconstruction:
Each phase is the **vector sum**:
- Va = V1 + V2 + V0  
- Vb = a²V1 + aV2 + V0  
- Vc = aV1 + a²V2 + V0  

### ⚡ Why important?
- Basis of **fault analysis (LG, LL, LLG)**  
- Used in **power system protection**  
""")
