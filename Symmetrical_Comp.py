import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Symmetrical Components", layout="wide")

st.title("⚡ Symmetrical Components Analyzer")

st.markdown("""
Convert **phase quantities (Va, Vb, Vc)** into:
- Positive sequence (V1)
- Negative sequence (V2)
- Zero sequence (V0)
""")

# ---------------- INPUT ----------------
st.sidebar.header("Phase Voltages (Magnitude & Angle)")

Va_mag = st.sidebar.slider("Va Magnitude", 0.0, 500.0, 230.0)
Va_ang = st.sidebar.slider("Va Angle (deg)", -180, 180, 0)

Vb_mag = st.sidebar.slider("Vb Magnitude", 0.0, 500.0, 230.0)
Vb_ang = st.sidebar.slider("Vb Angle (deg)", -180, 180, -120)

Vc_mag = st.sidebar.slider("Vc Magnitude", 0.0, 500.0, 230.0)
Vc_ang = st.sidebar.slider("Vc Angle (deg)", -180, 180, 120)

# ---------------- COMPLEX CONVERSION ----------------
def phasor(mag, angle_deg):
    return mag * np.exp(1j * np.deg2rad(angle_deg))

Va = phasor(Va_mag, Va_ang)
Vb = phasor(Vb_mag, Vb_ang)
Vc = phasor(Vc_mag, Vc_ang)

# Operator a
a = np.exp(1j * 2 * np.pi / 3)

# ---------------- SYMMETRICAL COMPONENTS ----------------
V0 = (Va + Vb + Vc) / 3
V1 = (Va + a*Vb + a**2 * Vc) / 3
V2 = (Va + a**2 * Vb + a * Vc) / 3

# ---------------- DISPLAY ----------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Sequence Components")

    st.write(f"**V0 (Zero Seq):** {abs(V0):.2f} ∠ {np.angle(V0, deg=True):.2f}°")
    st.write(f"**V1 (Positive Seq):** {abs(V1):.2f} ∠ {np.angle(V1, deg=True):.2f}°")
    st.write(f"**V2 (Negative Seq):** {abs(V2):.2f} ∠ {np.angle(V2, deg=True):.2f}°")

# ---------------- PHASOR PLOT ----------------
with col2:
    st.subheader("📉 Phasor Diagram")

    fig, ax = plt.subplots()

    def draw_phasor(V, label):
        ax.arrow(0, 0, V.real, V.imag, head_width=10, length_includes_head=True)
        ax.text(V.real, V.imag, label)

    draw_phasor(Va, "Va")
    draw_phasor(Vb, "Vb")
    draw_phasor(Vc, "Vc")

    ax.set_xlabel("Real")
    ax.set_ylabel("Imaginary")
    ax.axhline(0)
    ax.axvline(0)
    ax.grid(True)

    st.pyplot(fig)

# ---------------- RECONSTRUCTION CHECK ----------------
st.subheader("🔁 Reconstruction Check")

Va_rec = V0 + V1 + V2
Vb_rec = V0 + a**2 * V1 + a * V2
Vc_rec = V0 + a * V1 + a**2 * V2

st.write(f"Va reconstructed: {abs(Va_rec):.2f}")
st.write(f"Vb reconstructed: {abs(Vb_rec):.2f}")
st.write(f"Vc reconstructed: {abs(Vc_rec):.2f}")

# ---------------- THEORY ----------------
st.subheader("📘 Theory")

st.latex(r"V_0 = \frac{V_a + V_b + V_c}{3}")
st.latex(r"V_1 = \frac{V_a + aV_b + a^2V_c}{3}")
st.latex(r"V_2 = \frac{V_a + a^2V_b + aV_c}{3}")

st.markdown("""
### ⚡ Key Concepts:
- Positive sequence → balanced forward rotation
- Negative sequence → reverse rotation
- Zero sequence → in-phase components
- Used in fault analysis (LG, LL, LLG)
""")
