"""
LUCKY BANDIT v4.3 — Acoustic Impedance Matching & Resonance Analysis
=====================================================================
Calculates the critical acoustic parameters required for the PCT
patent specification: impedance matching, resonant modes, cavitation
thresholds, and Rayleigh-Plesset bubble dynamics.

All SI units unless noted.
"""

import math
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

# ===========================================================================
# 1. MATERIAL PROPERTIES
# ===========================================================================

# Vessel wall — SA-508 Grade 3 forged steel (typical pressure vessel steel)
rho_steel = 7850.0        # kg/m³ — density
c_steel = 5960.0           # m/s — longitudinal sound speed
Z_steel = rho_steel * c_steel  # Pa·s/m (Rayl) — acoustic impedance
E_steel = 210e9            # Pa — Young's modulus
sigma_y = 450e6            # Pa — yield strength (SA-508 Gr3)
sigma_uts = 620e6          # Pa — ultimate tensile strength

# Carrier fluid — mineral slurry (water + suspended solite ~30% w/w)
rho_slurry = 1450.0        # kg/m³ — typical gold-bearing slurry
c_slurry = 1520.0          # m/s — sound speed in dense slurry
Z_slurry = rho_slurry * c_slurry
P_vapor = 2340.0           # Pa — vapor pressure of water at 20°C
gamma_fluid = 0.072        # N/m — surface tension (water)
nu_fluid = 1.0e-6          # m²/s — kinematic viscosity

# Quartz gangue target
sigma_tensile_quartz = 48e6   # Pa — tensile strength of quartz
sigma_tensile_calcite = 12e6  # Pa — tensile strength of calcite
sigma_tensile_pyrite = 25e6   # Pa — tensile strength of pyrite

# ===========================================================================
# 2. VESSEL GEOMETRY
# ===========================================================================

wall_t = 0.075             # m — 75 mm wall thickness
ID = 1.700                 # m — inner diameter
OD = 1.850                 # m — outer diameter
straight_H = 2.800         # m — straight section height
exit_bore = 0.678          # m — bottom exit bore

# ===========================================================================
# 3. ACOUSTIC IMPEDANCE MATCHING
# ===========================================================================
print("=" * 70)
print("ACOUSTIC IMPEDANCE MATCHING ANALYSIS")
print("=" * 70)

# Impedance mismatch ratio
Z_ratio = Z_steel / Z_slurry
R_coeff = (Z_steel - Z_slurry) / (Z_steel + Z_slurry)  # reflection coefficient
T_coeff = 1 - R_coeff**2  # transmission coefficient (power)

print(f"\nZ_steel  = {Z_steel/1e6:.2f} MRayl")
print(f"Z_slurry = {Z_slurry/1e6:.2f} MRayl")
print(f"Impedance ratio Z_steel/Z_slurry = {Z_ratio:.1f}")
print(f"Reflection coefficient (amplitude) = {R_coeff:.4f}")
print(f"Power transmission coefficient     = {T_coeff:.4f}  ({T_coeff*100:.2f}%)")

# Half-wavelength resonance through the wall
# At f_half, wall thickness = λ_steel / 2 → wall is acoustically transparent
f_half = c_steel / (2 * wall_t)
print(f"\n*** HALF-WAVELENGTH WALL RESONANCE: f = {f_half:.1f} Hz "
      f"({f_half/1000:.2f} kHz) ***")
print(f"    At this frequency, the 75 mm wall is ACOUSTICALLY TRANSPARENT.")
print(f"    Wall thickness = λ_steel/2 = {c_steel/(2*f_half)*1000:.1f} mm ✓")

# Quarter-wavelength (maximum reflection)
f_quarter = c_steel / (4 * wall_t)
print(f"\nQuarter-wave blocking frequency: {f_quarter:.1f} Hz ({f_quarter/1000:.2f} kHz)")

# ===========================================================================
# 4. VESSEL INTERNAL RESONANT MODES
# ===========================================================================
print(f"\n{'=' * 70}")
print("VESSEL INTERNAL RESONANT MODES (cylindrical cavity)")
print("=" * 70)

# Axial modes: f_n = n * c / (2 * L)  for n = 1, 2, 3...
# Using straight section height as primary resonant length
print(f"\nAxial modes (straight section L = {straight_H} m):")
for n in range(1, 8):
    f_axial = n * c_slurry / (2 * straight_H)
    print(f"  n={n}: f = {f_axial:.1f} Hz")
    if abs(f_axial - 333) < 50:
        print(f"         ^^^ CLOSE TO 333 Hz DESIGN TARGET")

# Radial modes: f_mn = α_mn * c / (π * D)
# α_mn are zeros of Bessel function derivative J'_m
# First few: α_01=3.832, α_11=1.841, α_21=3.054, α_02=7.016
alphas = {"(0,1)": 3.832, "(1,1)": 1.841, "(2,1)": 3.054, "(0,2)": 7.016}
print(f"\nRadial modes (ID = {ID} m):")
for mode, alpha in alphas.items():
    f_radial = alpha * c_slurry / (math.pi * ID)
    print(f"  mode {mode}: f = {f_radial:.1f} Hz")

# ===========================================================================
# 5. CAVITATION NUMBER & THRESHOLD
# ===========================================================================
print(f"\n{'=' * 70}")
print("CAVITATION ANALYSIS")
print("=" * 70)

# Cavitation number: σ = (P_ref - P_vapor) / (0.5 * ρ * v²)
# For σ < 0.2, we need: v > sqrt((P_ref - P_vapor) / (0.1 * ρ))
# At vessel operating pressure P_op = 172.4 MPa (from spec)
P_op = 172.4e6  # Pa — operating pressure (dynamic acoustic shock rating)
# But the STATIC operating pressure for mineral processing is much lower
P_static = 2.0e6  # Pa — typical hydrocyclone operating pressure (~20 bar)

print(f"\nDesign pressure (dynamic shock rating): {P_op/1e6:.1f} MPa")
print(f"Static operating pressure: {P_static/1e6:.1f} MPa")

# Cavitation threshold velocity at static operating pressure
v_cav_threshold = math.sqrt((P_static - P_vapor) / (0.1 * rho_slurry))
print(f"\nFor σ = 0.2 (onset of cavitation):")
print(f"  Required flow velocity: v > {v_cav_threshold:.1f} m/s")

# Target cavitation number range (from patent claims)
for sigma_target in [0.05, 0.10, 0.15, 0.20]:
    v_req = math.sqrt((P_static - P_vapor) / (0.5 * rho_slurry * sigma_target))
    Re = v_req * ID / nu_fluid
    print(f"  σ = {sigma_target:.2f} → v = {v_req:.1f} m/s, "
          f"Re = {Re:.2e}")

# ===========================================================================
# 6. RAYLEIGH-PLESSET BUBBLE DYNAMICS
# ===========================================================================
print(f"\n{'=' * 70}")
print("RAYLEIGH-PLESSET BUBBLE COLLAPSE DYNAMICS")
print("=" * 70)

# Simplified Rayleigh-Plesset equation:
# R*R'' + (3/2)*R'² = (1/ρ) * [P_B(t) - P_∞(t)] - 4ν*R'/R - 2γ/(ρ*R)
#
# Where P_∞(t) = P_static + P_acoustic * sin(2πft)

R0 = 50e-6  # m — initial bubble radius (50 μm, typical cavitation nucleus)
P_acoustic = 0.5e6  # Pa — acoustic pressure amplitude

def rayleigh_plesset(t, y, f_drive, P_ac):
    """Rayleigh-Plesset ODE system: y = [R, dR/dt]"""
    R, Rdot = y
    if R < 1e-9:  # prevent singularity
        R = 1e-9

    # Internal bubble pressure (adiabatic, γ=1.4 for air)
    P_B = (P_vapor + 2 * gamma_fluid / R0) * (R0 / R) ** (3 * 1.4)

    # Far-field pressure with acoustic driving
    P_inf = P_static + P_ac * math.sin(2 * math.pi * f_drive * t)

    # Rayleigh-Plesset
    Rddot = (1.0 / R) * (
        (P_B - P_inf) / rho_slurry
        - 1.5 * Rdot**2
        - 4 * nu_fluid * Rdot / R
        - 2 * gamma_fluid / (rho_slurry * R)
    )

    return [Rdot, Rddot]


# Solve for the design frequency (333 Hz) and the wall-resonance frequency
frequencies_to_test = {
    "333 Hz (fundamental resonator)": 333.0,
    "~271 Hz (n=1 axial mode)": c_slurry / (2 * straight_H),
    "~39.7 kHz (wall transparency)": f_half,
}

for label, f_test in frequencies_to_test.items():
    period = 1.0 / f_test
    t_span = (0, 5 * period)
    t_eval = np.linspace(0, 5 * period, 5000)

    try:
        sol = solve_ivp(
            rayleigh_plesset,
            t_span,
            [R0, 0.0],
            args=(f_test, P_acoustic),
            t_eval=t_eval,
            method='RK45',
            max_step=period / 200,
            rtol=1e-8,
            atol=1e-12,
        )

        R_min = np.min(sol.y[0])
        R_max = np.max(sol.y[0])
        compression_ratio = R0 / R_min if R_min > 0 else float('inf')

        # Estimate collapse pressure (water hammer): P_collapse ≈ ρ * c * v_jet
        # Maximum wall velocity
        Rdot_max = np.max(np.abs(sol.y[1]))
        P_collapse = rho_slurry * c_slurry * Rdot_max

        print(f"\n  {label}:")
        print(f"    R_min = {R_min*1e6:.2f} μm, R_max = {R_max*1e6:.2f} μm")
        print(f"    Compression ratio R0/R_min = {compression_ratio:.1f}")
        print(f"    Max wall velocity |dR/dt| = {Rdot_max:.1f} m/s")
        print(f"    Est. collapse pressure = {P_collapse/1e6:.1f} MPa "
              f"({P_collapse/1e9:.2f} GPa)")
        print(f"    Exceeds quartz tensile ({sigma_tensile_quartz/1e6:.0f} MPa)? "
              f"{'YES ✓' if P_collapse > sigma_tensile_quartz else 'NO ✗'}")
    except Exception as e:
        print(f"\n  {label}: Solver failed — {e}")

# ===========================================================================
# 7. ACOUSTIC POWER BUDGET
# ===========================================================================
print(f"\n{'=' * 70}")
print("ACOUSTIC POWER BUDGET")
print("=" * 70)

# Acoustic intensity: I = P²/(2ρc)
I_acoustic = P_acoustic**2 / (2 * rho_slurry * c_slurry)
print(f"\nAcoustic pressure amplitude: {P_acoustic/1e6:.2f} MPa")
print(f"Acoustic intensity: {I_acoustic:.1f} W/m²")

# MCZ (Maximal Cavitation Zone) — approximate as annular region
# near the taper-to-straight transition
MCZ_r_inner = 0.300  # m — inner radius of MCZ
MCZ_r_outer = 0.500  # m — outer radius of MCZ
MCZ_area = math.pi * (MCZ_r_outer**2 - MCZ_r_inner**2)
P_total = I_acoustic * MCZ_area
print(f"MCZ annular area: {MCZ_area:.3f} m²")
print(f"Total acoustic power to MCZ: {P_total:.1f} W ({P_total/1000:.2f} kW)")

# Transducer count estimate (typical piezo: 50-500 W each)
transducer_power = 200  # W per transducer
n_transducers = math.ceil(P_total / transducer_power)
print(f"Estimated transducers needed (~{transducer_power}W each): {n_transducers}")

# ===========================================================================
# 8. SUMMARY TABLE FOR PCT SPECIFICATION
# ===========================================================================
print(f"\n{'=' * 70}")
print("PCT SPECIFICATION — KEY PARAMETERS")
print("=" * 70)

params = [
    ("Vessel OD", f"{OD*1000:.0f} mm"),
    ("Vessel ID", f"{ID*1000:.0f} mm"),
    ("Wall thickness", f"{wall_t*1000:.0f} mm"),
    ("Wall material", "SA-508 Grade 3 forged steel"),
    ("Design pressure (dynamic)", f"{P_op/1e6:.1f} MPa"),
    ("Operating pressure (static)", f"{P_static/1e6:.1f} MPa"),
    ("Acoustic impedance — wall", f"{Z_steel/1e6:.2f} MRayl"),
    ("Acoustic impedance — slurry", f"{Z_slurry/1e6:.2f} MRayl"),
    ("Wall transparency frequency", f"{f_half:.1f} Hz ({f_half/1000:.2f} kHz)"),
    ("Primary resonator frequency", "333 Hz"),
    ("Vessel axial mode n=1", f"{c_slurry/(2*straight_H):.1f} Hz"),
    ("Cavitation number range", "0.05 – 0.15"),
    ("Reynolds number range", f"> {v_cav_threshold * ID / nu_fluid:.2e}"),
    ("Acoustic pressure amplitude", f"{P_acoustic/1e6:.2f} MPa"),
    ("Carrier fluid density", f"{rho_slurry:.0f} kg/m³"),
    ("Target mineral tensile strength", f"{sigma_tensile_quartz/1e6:.0f} MPa (quartz)"),
]

for name, val in params:
    print(f"  {name:<35s} {val}")

print(f"\n{'=' * 70}")
print("Analysis complete. Values above are for PCT Specification §2-4.")
print("=" * 70)
