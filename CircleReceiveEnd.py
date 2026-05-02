# ======================================================================
# RECEIVING END CIRCLE DIAGRAM OF TRANSMISSION LINE
# THEORETICALLY CORRECT RECEIVING END POWER CIRCLE
# FIX:
# ✅ Correct centre = A|Vr|² / |B|
# ✅ Origin and centre are different
# ✅ Proper power circle geometry
# ✅ Origin → Centre
# ✅ Origin → Operating Point
# ✅ Centre → Operating Point
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

# ----------------------------------------------------------------------
# BACKGROUND
# ----------------------------------------------------------------------
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
    min_value=1.0,
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
    "B Magnitude |B| (Ω)",
    min_value=0.001,
    max_value=5000.0,
    value=80.0,
    step=1.0,
    format="%.4f"
)

B_ang = st.sidebar.number_input(
    "B Angle β (deg)",
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
# PER PHASE VALUES
# ----------------------------------------------------------------------
Vr_phase = (Vr * 1e3) / np.sqrt(3)

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
# SENDING END VOLTAGE
# ----------------------------------------------------------------------
Vs = A * Vr_phasor + B * Ir_phasor

Vs_mag = np.abs(Vs) * np.sqrt(3) / 1000

# ----------------------------------------------------------------------
# RECEIVING END POWER
# ----------------------------------------------------------------------
S_r = 3 * Vr_phasor * np.conj(Ir_phasor)

P_r = np.real(S_r) / 1e6
Q_r = np.imag(S_r) / 1e6

# ----------------------------------------------------------------------
# TRUE RECEIVING END CIRCLE CENTRE
# Centre = -(3 A Vr² / B)
# ----------------------------------------------------------------------
beta = np.radians(B_ang)

K = (3 * A_mag * (Vr_phase ** 2)) / B_mag
K_MW = K / 1e6

center_x = -K_MW * np.cos(beta)
center_y = -K_MW * np.sin(beta)

# ----------------------------------------------------------------------
# RADIUS
# ----------------------------------------------------------------------
radius = np.sqrt((P_r - center_x) ** 2 + (Q_r - center_y) ** 2)

# ----------------------------------------------------------------------
# CIRCLE LOCUS USING TRUE CENTRE
# ----------------------------------------------------------------------
theta = np.linspace(0, 2 * np.pi, 1000)

P_circle = center_x + radius * np.cos(theta)
Q_circle = center_y + radius * np.sin(theta)

# ----------------------------------------------------------------------
# VOLTAGE REGULATION
# ----------------------------------------------------------------------
VR_percent = ((Vs_mag - Vr) / Vr) * 100

# ----------------------------------------------------------------------
# LAYOUT
# ----------------------------------------------------------------------
col1, col2 = st.columns([1.5, 1])

# ======================================================================
# CIRCLE DIAGRAM
# ======================================================================
with col1:
    st.subheader("📈 Receiving End Circle Diagram")

    fig, ax = plt.subplots(figsize=(10, 9))

    # Circle
    ax.plot(
        P_circle,
        Q_circle,
        color="blue",
        linewidth=3,
        label="Receiving End Circle"
    )

    # Origin
    ax.scatter(
        0,
        0,
        color="black",
        marker="x",
        s=120,
        zorder=7,
        label="Origin"
    )

    # Centre
    ax.scatter(
        center_x,
        center_y,
        color="purple",
        s=100,
        zorder=7,
        label="Centre"
    )

    # Operating Point
    ax.scatter(
        P_r,
        Q_r,
        color="red",
        s=120,
        zorder=8,
        label="Operating Point"
    )

    # Origin → Centre
    ax.plot(
        [0, center_x],
        [0, center_y],
        linestyle=":",
        linewidth=3,
        color="purple",
        label="Origin → Centre"
    )

    # Origin → Operating Point
    ax.plot(
        [0, P_r],
        [0, Q_r],
        linestyle="--",
        linewidth=3,
        color="green",
        label="Origin → Operating Point"
    )

    # Centre → Operating Point
    ax.plot(
        [center_x, P_r],
        [center_y, Q_r],
        linestyle="-.",
        linewidth=3,
        color="orange",
        label="Centre → Operating Point"
    )

    # Labels
    ax.annotate(
        "Origin",
        (0, 0),
        xytext=(10, 10),
        textcoords="offset points"
    )

    ax.annotate(
        "Centre",
        (center_x, center_y),
        xytext=(10, -15),
        textcoords="offset points"
    )

    ax.annotate(
        f"Operating Point\nPF={pf:.2f}",
        (P_r, Q_r),
        xytext=(20, 20),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->")
    )

    # Axes
    ax.axhline(0, linestyle="--", color="black")
    ax.axvline(0, linestyle="--", color="black")

    max_range = max(
        np.max(np.abs(P_circle)),
        np.max(np.abs(Q_circle)),
        abs(P_r),
        abs(Q_r),
        abs(center_x),
        abs(center_y)
    ) * 1.2

    ax.set_xlim(-max_range, max_range)
    ax.set_ylim(-max_range, max_range)

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

    ax2.arrow(
        0, 0,
        np.real(Vr_phasor) / 1000,
        np.imag(Vr_phasor) / 1000,
        head_width=5,
        length_includes_head=True
    )

    ax2.arrow(
        0, 0,
        np.real(Vs) / 1000,
        np.imag(Vs) / 1000,
        head_width=5,
        length_includes_head=True
    )

    ax2.text(np.real(Vr_phasor)/1000, np.imag(Vr_phasor)/1000, "Vr")
    ax2.text(np.real(Vs)/1000, np.imag(Vs)/1000, "Vs")

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

r1, r2, r3, r4 = st.columns(4)

r1.metric("Receiving Real Power", f"{P_r:.2f} MW")
r2.metric("Receiving Reactive Power", f"{Q_r:.2f} MVAR")
r3.metric("Sending End Voltage", f"{Vs_mag:.2f} kV")
r4.metric("Voltage Regulation", f"{VR_percent:.2f} %")

# ======================================================================
# THEORY
# ======================================================================
st.divider()
st.subheader("📘 Circle Theory")

st.markdown("""
### Receiving End Circle Centre:
Centre = -(3 A Vr² / B)

### Radius:
Radius = Distance from Centre to Operating Point

### Key Vectors:
- Origin → Centre
- Origin → Operating Point
- Centre → Operating Point
""")

# ======================================================================
# FOOTER
# ======================================================================
st.caption("Developed for Power System Visualization ⚡")
