# ======================================================================
# RECEIVING END CIRCLE DIAGRAM OF TRANSMISSION LINE
# Streamlit App
# Features:
# ✅ ABCD parameter inputs
# ✅ Receiving-end circle diagram
# ✅ Operating point
# ✅ Lagging / Leading PF
# ✅ Voltage regulation
# ✅ Real / Reactive power visualization
# ======================================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Receiving End Circle Diagram",
    page_icon="⚡",
    layout="wide"
)

# Gradient background
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #dbeafe 0%, #f0f9ff 100%);
}
</style>
""", unsafe_allow_html=True)

st.title("⚡ Receiving End Circle Diagram of Transmission Line")

# ----------------------------------------------------------------------
# SIDEBAR INPUTS
# ----------------------------------------------------------------------
st.sidebar.header("🔧 Transmission Line Parameters")

Vr = st.sidebar.number_input(
    "Receiving End Voltage |Vr| (kV)",
    min_value=0.0,
    max_value=1000.0,
    value=220.0,
    step=1.0,
    format="%.2f"
)

st.sidebar.subheader("📘 ABCD Parameters")

A_mag = st.sidebar.number_input(
    "A Magnitude",
    min_value=0.0,
    max_value=5.0,
    value=1.0,
    step=0.01,
    format="%.4f"
)

A_ang = st.sidebar.number_input(
    "A Angle (deg)",
    min_value=-180.0,
    max_value=180.0,
    value=0.0,
    step=0.1,
    format="%.2f"
)

B_mag = st.sidebar.number_input(
    "B Magnitude (Ω)",
    min_value=0.0,
    max_value=5000.0,
    value=80.0,
    step=1.0,
    format="%.4f"
)

B_ang = st.sidebar.number_input(
    "B Angle (deg)",
    min_value=-180.0,
    max_value=180.0,
    value=80.0,
    step=0.1,
    format="%.2f"
)


S_MVA = st.sidebar.number_input(
    "Receiving End Apparent Power (MVA)",
    min_value=0.0,
    max_value=5000.0,
    value=100.0,
    step=1.0,
    format="%.2f"
)
pf = st.sidebar.slider("Receiving End Power Factor", 0.0, 1.0, 0.8)
# ----------------------------------------------------------------------
# CONVERT POWER TO CURRENT
# 3-phase formula:
# S = √3 × V × I
# I = S / (√3 × V)
# Vr in kV, S in MVA → I in A
# ----------------------------------------------------------------------

Ir = (S_MVA * 1e6) / (np.sqrt(3) * Vr * 1e3)



mode = st.sidebar.radio("Load Type", ["Lagging", "Leading"])

# ----------------------------------------------------------------------
# PHASOR CONVERSION
# ----------------------------------------------------------------------
A = A_mag * np.exp(1j * np.radians(A_ang))
B = B_mag * np.exp(1j * np.radians(B_ang))

Vr_phasor = Vr * np.exp(1j * 0)

phi = np.arccos(pf)

if mode == "Lagging":
    Ir_phasor = Ir * np.exp(-1j * phi)
else:
    Ir_phasor = Ir * np.exp(1j * phi)

# ----------------------------------------------------------------------
# SENDING END VOLTAGE
# ----------------------------------------------------------------------
Vs = A * Vr_phasor + B * Ir_phasor

Vs_mag = np.abs(Vs)

# Voltage Regulation
VR_percent = ((Vs_mag - Vr) / Vr) * 100

# ----------------------------------------------------------------------
# POWER
# ----------------------------------------------------------------------
S_r = Vr_phasor * np.conj(Ir_phasor)

P_r = np.real(S_r)
Q_r = np.imag(S_r)

# ----------------------------------------------------------------------
# RECEIVING END CIRCLE LOCUS
# ----------------------------------------------------------------------
theta = np.linspace(-np.pi, np.pi, 500)

circle_current = Ir * np.exp(1j * theta)

Vs_circle = A * Vr_phasor + B * circle_current

# Power coordinates
P_circle = np.real(Vr_phasor * np.conj(circle_current))
Q_circle = np.imag(Vr_phasor * np.conj(circle_current))

# ----------------------------------------------------------------------
# LAYOUT
# ----------------------------------------------------------------------
col1, col2 = st.columns([1.4, 1])

# ======================================================================
# CIRCLE DIAGRAM
# ======================================================================
with col1:
    st.subheader("📈 Receiving End Power Circle Diagram")

    fig, ax = plt.subplots(figsize=(9, 8))

    # Circle locus
    ax.plot(P_circle, Q_circle, linewidth=2, label="Receiving End Circle")

    # Operating point
    ax.plot(P_r, Q_r, 'ro', markersize=8, label="Operating Point")

    ax.annotate(
        f"PF={pf:.2f}",
        (P_r, Q_r),
        xytext=(15, 15),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->")
    )

    # Axes
    ax.axhline(0, linestyle="--")
    ax.axvline(0, linestyle="--")

    ax.set_xlabel("Real Power P (kW approx)")
    ax.set_ylabel("Reactive Power Q (kVAR approx)")
    ax.set_title("Receiving End Circle Diagram")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig)

# ======================================================================
# PHASOR DIAGRAM
# ======================================================================
with col2:
    st.subheader("🧭 Voltage Phasor Diagram")

    fig2, ax2 = plt.subplots(figsize=(7, 7))

    # Vr
    ax2.arrow(
        0, 0,
        np.real(Vr_phasor),
        np.imag(Vr_phasor),
        head_width=5,
        length_includes_head=True,
        label="Vr"
    )

    # Vs
    ax2.arrow(
        0, 0,
        np.real(Vs),
        np.imag(Vs),
        head_width=5,
        length_includes_head=True
    )

    ax2.text(np.real(Vr_phasor), np.imag(Vr_phasor), "Vr")
    ax2.text(np.real(Vs), np.imag(Vs), "Vs")

    ax2.axhline(0, linestyle="--")
    ax2.axvline(0, linestyle="--")

    lim = max(Vs_mag, Vr) * 1.2

    ax2.set_xlim(-lim * 0.2, lim)
    ax2.set_ylim(-lim * 0.8, lim * 0.8)

    ax2.set_aspect("equal")
    ax2.grid(True)

    st.pyplot(fig2)

# ======================================================================
# RESULTS PANEL
# ======================================================================
st.divider()
st.subheader("📊 Calculated Results")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Receiving Real Power P", f"{P_r:.2f}")
m2.metric("Receiving Reactive Power Q", f"{Q_r:.2f}")
m3.metric("Sending Voltage |Vs|", f"{Vs_mag:.2f} kV")
m4.metric("Voltage Regulation", f"{VR_percent:.2f} %")

# ======================================================================
# THEORY
# ======================================================================
st.divider()
st.subheader("📘 Key Formula")

st.markdown("""
### Sending End Voltage:
Vs = A·Vr + B·Ir

### Voltage Regulation:
%VR = ((|Vs| - |Vr|)/|Vr|) × 100

### Receiving End Complex Power:
S = Vr × Ir*
""")

# ======================================================================
# STATUS
# ======================================================================
if VR_percent > 0:
    st.warning("⚠️ Positive regulation: Sending voltage exceeds receiving voltage")
else:
    st.success("✅ Negative regulation / Ferranti effect region")

# ======================================================================
# EXTRA INSIGHTS
# ======================================================================
with st.expander("💡 Engineering Insight"):
    st.write("""
### Lagging Power Factor:
- Higher reactive demand
- Larger voltage drop
- Poorer regulation

### Leading Power Factor:
- Better voltage support
- Can reduce regulation
- May cause Ferranti effect
""")

# ======================================================================
# FOOTER
# ======================================================================
st.caption("Developed for Power System Visualization ⚡")
