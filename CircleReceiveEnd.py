# ======================================================================
# RECEIVING END CIRCLE DIAGRAM OF TRANSMISSION LINE
# CORRECTED VERSION
# FIXES:
# ✅ Proper 3-phase power calculations
# ✅ Per-phase ABCD model
# ✅ Correct MW / MVAR scaling
# ✅ Accurate sending voltage
# ✅ Proper voltage regulation
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

# Background
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #dbeafe 0%, #f0f9ff 100%);
}
</style>
""", unsafe_allow_html=True)

st.title("⚡ Receiving End Circle Diagram of Transmission Line")

# ----------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------
st.sidebar.header("🔧 Transmission Line Parameters")

# Receiving voltage (Line-Line)
Vr = st.sidebar.number_input(
    "Receiving End Voltage |Vr| (kV)",
    min_value=1.0,
    max_value=1000.0,
    value=220.0,
    step=1.0,
    format="%.2f"
)

# ABCD
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

# Load
S_MVA = st.sidebar.number_input(
    "Receiving End Apparent Power (MVA)",
    min_value=0.0,
    max_value=5000.0,
    value=100.0,
    step=1.0,
    format="%.2f"
)

pf = st.sidebar.slider(
    "Receiving End Power Factor",
    min_value=0.0,
    max_value=1.0,
    value=0.8
)

mode = st.sidebar.radio(
    "Load Type",
    ["Lagging", "Leading"]
)

# ----------------------------------------------------------------------
# PER-PHASE CONVERSION
# ----------------------------------------------------------------------
Vr_phase = (Vr * 1e3) / np.sqrt(3)   # volts

# 3-phase current
Ir = (S_MVA * 1e6) / (np.sqrt(3) * Vr * 1e3)

# ----------------------------------------------------------------------
# ABCD PHASORS
# ----------------------------------------------------------------------
A = A_mag * np.exp(1j * np.radians(A_ang))
B = B_mag * np.exp(1j * np.radians(B_ang))

Vr_phasor = Vr_phase + 0j

phi = np.arccos(pf)

if mode == "Lagging":
    Ir_phasor = Ir * np.exp(-1j * phi)
else:
    Ir_phasor = Ir * np.exp(1j * phi)

# ----------------------------------------------------------------------
# SENDING END
# ----------------------------------------------------------------------
Vs = A * Vr_phasor + B * Ir_phasor

# Convert to line voltage
Vs_mag = (np.abs(Vs) * np.sqrt(3)) / 1000  # kV

# Voltage regulation
VR_percent = ((Vs_mag - Vr) / Vr) * 100

# ----------------------------------------------------------------------
# RECEIVING END POWER (3-phase)
# ----------------------------------------------------------------------
S_r = 3 * Vr_phasor * np.conj(Ir_phasor)

P_r = np.real(S_r) / 1e6   # MW
Q_r = np.imag(S_r) / 1e6   # MVAR

# ----------------------------------------------------------------------
# POWER CIRCLE
# ----------------------------------------------------------------------
theta = np.linspace(-np.pi, np.pi, 800)

circle_current = Ir * np.exp(1j * theta)

S_circle = 3 * Vr_phasor * np.conj(circle_current)

P_circle = np.real(S_circle) / 1e6
Q_circle = np.imag(S_circle) / 1e6

# ----------------------------------------------------------------------
# LAYOUT
# ----------------------------------------------------------------------
col1, col2 = st.columns([1.4, 1])

# ======================================================================
# RECEIVING END CIRCLE
# ======================================================================
with col1:
    st.subheader("📈 Receiving End Circle Diagram")

    fig, ax = plt.subplots(figsize=(9, 8))

    # Circle
    ax.plot(
        P_circle,
        Q_circle,
        linewidth=2.5,
        label="Receiving End Power Circle"
    )

    # Operating point
    ax.plot(
        P_r,
        Q_r,
        'ro',
        markersize=8,
        label="Operating Point"
    )

    ax.annotate(
        f"PF = {pf:.2f}",
        (P_r, Q_r),
        xytext=(15, 15),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->")
    )

    # Axis
    ax.axhline(0, linestyle="--")
    ax.axvline(0, linestyle="--")

    ax.set_xlabel("Real Power P (MW)")
    ax.set_ylabel("Reactive Power Q (MVAR)")
    ax.set_title("Receiving End Power Circle Diagram")

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
        0,
        0,
        np.real(Vr_phasor) / 1000,
        np.imag(Vr_phasor) / 1000,
        head_width=5,
        length_includes_head=True
    )

    # Vs
    ax2.arrow(
        0,
        0,
        np.real(Vs) / 1000,
        np.imag(Vs) / 1000,
        head_width=5,
        length_includes_head=True
    )

    ax2.text(
        np.real(Vr_phasor) / 1000,
        np.imag(Vr_phasor) / 1000,
        "Vr"
    )

    ax2.text(
        np.real(Vs) / 1000,
        np.imag(Vs) / 1000,
        "Vs"
    )

    ax2.axhline(0, linestyle="--")
    ax2.axvline(0, linestyle="--")

    lim = max(np.abs(Vs), np.abs(Vr_phasor)) / 1000 * 1.3

    ax2.set_xlim(-lim * 0.3, lim)
    ax2.set_ylim(-lim, lim)

    ax2.set_aspect("equal")
    ax2.grid(True)

    st.pyplot(fig2)

# ======================================================================
# RESULTS
# ======================================================================
st.divider()
st.subheader("📊 Calculated Results")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Receiving Real Power", f"{P_r:.2f} MW")
m2.metric("Receiving Reactive Power", f"{Q_r:.2f} MVAR")
m3.metric("Sending End Voltage", f"{Vs_mag:.2f} kV")
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
S = 3 × Vr × Ir*
""")

# ======================================================================
# STATUS
# ======================================================================
if VR_percent > 0:
    st.warning("⚠️ Positive Regulation: Sending voltage is higher than receiving voltage")
elif VR_percent < 0:
    st.success("✅ Negative Regulation / Ferranti Effect Region")
else:
    st.info("ℹ️ Zero Voltage Regulation")

# ======================================================================
# ENGINEERING INSIGHT
# ======================================================================
with st.expander("💡 Engineering Insight"):
    st.write("""
### Lagging Load:
- Higher reactive demand
- More voltage drop
- Poor voltage regulation

### Leading Load:
- Voltage support improves
- Can reduce or reverse regulation
- Excessive leading PF may cause Ferranti effect

### ABCD Notes:
- A ≈ D
- B = Series impedance effect
- C = Shunt admittance effect
""")

# ======================================================================
# FOOTER
# ======================================================================
st.caption("Developed for Power System Visualization ⚡")
