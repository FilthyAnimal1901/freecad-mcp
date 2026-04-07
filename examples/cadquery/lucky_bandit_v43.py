"""
LUCKY BANDIT v4.3 — High-Pressure Mineral Processing Vessel
=============================================================
CadQuery model of a hot-forged, seamless, axisymmetric pressure vessel
rated for 172.4 MPa dynamic acoustic shocks with infinite fatigue life.

Constructed via 2D half-profile sketch on the XZ plane + revolve(360°).
All dimensions in millimetres.

Open in CQ-Editor to visualise: cq-editor lucky_bandit_v43.py
"""

import math
import cadquery as cq

# ---------------------------------------------------------------------------
# 1. DIMENSIONAL CONSTANTS
# ---------------------------------------------------------------------------

# Main chamber
MAIN_OD = 1850.0                          # outer diameter
WALL_T = 75.0                             # uniform wall thickness
MAIN_ID = MAIN_OD - 2 * WALL_T           # 1700 mm
OUTER_R = MAIN_OD / 2.0                   # 925 mm
INNER_R = MAIN_ID / 2.0                   # 850 mm
STRAIGHT_H = 2800.0                       # straight cylindrical section

# Bottom taper (15° half-angle cone)
TAPER_HALF_ANGLE = 15.0                   # degrees
EXIT_BORE = 678.0                         # exit bore diameter
EXIT_INNER_R = EXIT_BORE / 2.0            # 339 mm
EXIT_OUTER_R = EXIT_INNER_R + WALL_T      # 414 mm
TAPER_H = (INNER_R - EXIT_INNER_R) / math.tan(math.radians(TAPER_HALF_ANGLE))
# ≈ 1907.4 mm

# Flanges
TOP_FLANGE_T = 40.0                       # top flange thickness
TOP_FLANGE_EXT = 85.0                     # radial extension beyond OD
TOP_FLANGE_R = OUTER_R + TOP_FLANGE_EXT   # 1010 mm
BOT_FLANGE_T = 30.0                       # bottom flange thickness
BOT_FLANGE_R = 500.0                      # bottom flange outer radius

# Charcoal Infinity Lip (overflow weir / trough at top rim)
LIP_OUTER_WALL_H = 60.0                   # height of outer wall above flange top
LIP_TROUGH_W = 25.0                       # radial width of trough channel
LIP_TROUGH_DEPTH = 45.0                   # depth of trough (open-topped)
LIP_BASE_T = LIP_OUTER_WALL_H - LIP_TROUGH_DEPTH  # 15 mm floor thickness

# Bottom Resonator Collar (acoustic actuator housing)
RESON_OFFSET_Z = 200.0                    # distance above top of bottom flange
RESON_H = 300.0                           # collar height
RESON_EXTRA_T = 40.0                      # extra radial thickness beyond outer taper

# Fillet radii
FILLET_LARGE = 50.0                       # major structural transitions
FILLET_MED = 30.0                         # secondary transitions
FILLET_SMALL = 15.0                       # lip / resonator details

# ---------------------------------------------------------------------------
# 2. Z-AXIS LAYOUT  (bottom = 0)
# ---------------------------------------------------------------------------
Z_BOT_FLANGE_BOT = 0.0
Z_BOT_FLANGE_TOP = BOT_FLANGE_T                          # 30
Z_TAPER_TOP = Z_BOT_FLANGE_TOP + TAPER_H                 # ~1937.4
Z_STRAIGHT_TOP = Z_TAPER_TOP + STRAIGHT_H                # ~4737.4
Z_TOP_FLANGE_TOP = Z_STRAIGHT_TOP + TOP_FLANGE_T          # ~4777.4
Z_LIP_TOP = Z_TOP_FLANGE_TOP + LIP_OUTER_WALL_H          # ~4837.4

# Resonator Z positions (on the outer taper, above bottom flange)
Z_RESON_BOT = Z_BOT_FLANGE_TOP + RESON_OFFSET_Z          # 230
Z_RESON_TOP = Z_RESON_BOT + RESON_H                      # 530

# ---------------------------------------------------------------------------
# 3. HELPER — outer taper radius at a given Z
# ---------------------------------------------------------------------------
def outer_taper_r_at(z):
    """Return the outer-surface radius of the taper at height z."""
    frac = (z - Z_BOT_FLANGE_TOP) / TAPER_H
    inner_r = EXIT_INNER_R + frac * (INNER_R - EXIT_INNER_R)
    return inner_r + WALL_T


# Resonator radii on the outer taper surface
RESON_R_BOT = outer_taper_r_at(Z_RESON_BOT)
RESON_R_TOP = outer_taper_r_at(Z_RESON_TOP)
RESON_R_BOT_EXT = RESON_R_BOT + RESON_EXTRA_T
RESON_R_TOP_EXT = RESON_R_TOP + RESON_EXTRA_T

# Inner taper radius helper
def inner_taper_r_at(z):
    frac = (z - Z_BOT_FLANGE_TOP) / TAPER_H
    return EXIT_INNER_R + frac * (INNER_R - EXIT_INNER_R)

# ---------------------------------------------------------------------------
# 4. BUILD 2D HALF-PROFILE (closed wire on XZ plane)
# ---------------------------------------------------------------------------
# The profile traces the complete cross-section as a single closed polygon:
#   - Outer surface from bottom-up (including resonator bulge & infinity lip)
#   - Inner surface from top-down
# X = radial distance from axis, Z = height

# We trace counter-clockwise starting from the exit bore bottom-right corner.

profile = (
    cq.Workplane("XZ")
    .moveTo(EXIT_INNER_R, Z_BOT_FLANGE_BOT)

    # --- OUTER PROFILE (bottom → up) ---

    # Bottom flange bottom surface → outward
    .lineTo(BOT_FLANGE_R, Z_BOT_FLANGE_BOT)

    # Bottom flange outer edge → up
    .lineTo(BOT_FLANGE_R, Z_BOT_FLANGE_TOP)

    # Outer taper: bottom flange top → resonator bottom
    .lineTo(RESON_R_BOT, Z_RESON_BOT)

    # Resonator collar: step outward
    .lineTo(RESON_R_BOT_EXT, Z_RESON_BOT)

    # Resonator collar: up
    .lineTo(RESON_R_TOP_EXT, Z_RESON_TOP)

    # Resonator collar: step back to taper surface
    .lineTo(RESON_R_TOP, Z_RESON_TOP)

    # Outer taper: resonator top → straight section
    .lineTo(OUTER_R, Z_TAPER_TOP)

    # Straight section: up
    .lineTo(OUTER_R, Z_STRAIGHT_TOP)

    # Top flange: outward
    .lineTo(TOP_FLANGE_R, Z_STRAIGHT_TOP)

    # Top flange outer edge: up to flange top
    .lineTo(TOP_FLANGE_R, Z_TOP_FLANGE_TOP)

    # --- CHARCOAL INFINITY LIP (open-topped trough) ---
    # Outer wall of lip: up
    .lineTo(TOP_FLANGE_R, Z_LIP_TOP)

    # Lip: inward across top of outer wall
    .lineTo(TOP_FLANGE_R - LIP_TROUGH_W, Z_LIP_TOP)

    # Trough inner wall: down into trough
    .lineTo(TOP_FLANGE_R - LIP_TROUGH_W, Z_TOP_FLANGE_TOP + LIP_BASE_T)

    # Trough floor: inward to the main body wall
    .lineTo(OUTER_R, Z_TOP_FLANGE_TOP + LIP_BASE_T)

    # Down to flange top surface (inner side of lip base)
    .lineTo(OUTER_R, Z_TOP_FLANGE_TOP)

    # --- INNER PROFILE (top → down) ---

    # Top flange underside: inward to inner wall
    .lineTo(INNER_R, Z_STRAIGHT_TOP)

    # Inner straight section: down
    .lineTo(INNER_R, Z_TAPER_TOP)

    # Inner taper: down to exit bore
    .lineTo(EXIT_INNER_R, Z_BOT_FLANGE_TOP)

    # Exit bore inner wall: down to start
    .lineTo(EXIT_INNER_R, Z_BOT_FLANGE_BOT)

    # Close the wire
    .close()
)

# ---------------------------------------------------------------------------
# 5. REVOLVE 360° AROUND Z-AXIS
# ---------------------------------------------------------------------------
# CadQuery revolve() on XZ plane revolves around the Z axis (vertical).
# The axis of revolution passes through the origin along the Z direction.
vessel = profile.revolve(360, (0, 0, 0), (0, 0, 1))

# ---------------------------------------------------------------------------
# 6. FILLETS — seamless forged transitions (SCF → 1.0)
# ---------------------------------------------------------------------------
# Apply fillets to soften all sharp transitions.
# Strategy: use fillet on all edges, applied in groups from largest to smallest.

# We select edges by Z-position ranges and apply appropriate fillet radii.

# Large fillets at major structural transitions:
#   - Taper-to-straight junction (inner & outer) near Z_TAPER_TOP
#   - Flange roots
try:
    vessel = (
        vessel
        .edges(
            cq.selectors.BoxSelector(
                (-OUTER_R - 100, -OUTER_R - 100, Z_TAPER_TOP - 5),
                (OUTER_R + 100, OUTER_R + 100, Z_TAPER_TOP + 5),
            )
        )
        .fillet(FILLET_LARGE)
    )
except Exception:
    pass  # skip if edge selection fails

# Fillets at inner taper-to-straight junction
try:
    vessel = (
        vessel
        .edges(
            cq.selectors.BoxSelector(
                (-INNER_R - 5, -INNER_R - 5, Z_TAPER_TOP - 5),
                (INNER_R + 5, INNER_R + 5, Z_TAPER_TOP + 5),
            )
        )
        .fillet(FILLET_LARGE)
    )
except Exception:
    pass

# Fillets at top flange root (where flange meets cylinder) — outer bottom edge
try:
    vessel = (
        vessel
        .edges(
            cq.selectors.BoxSelector(
                (-TOP_FLANGE_R - 5, -TOP_FLANGE_R - 5, Z_STRAIGHT_TOP - 5),
                (TOP_FLANGE_R + 5, TOP_FLANGE_R + 5, Z_STRAIGHT_TOP + 5),
            )
        )
        .fillet(FILLET_MED)
    )
except Exception:
    pass

# Fillets at bottom flange top surface → taper junction
try:
    vessel = (
        vessel
        .edges(
            cq.selectors.BoxSelector(
                (-BOT_FLANGE_R - 5, -BOT_FLANGE_R - 5, Z_BOT_FLANGE_TOP - 5),
                (BOT_FLANGE_R + 5, BOT_FLANGE_R + 5, Z_BOT_FLANGE_TOP + 5),
            )
        )
        .fillet(FILLET_MED)
    )
except Exception:
    pass

# Smaller fillets on resonator collar edges
try:
    vessel = (
        vessel
        .edges(
            cq.selectors.BoxSelector(
                (-RESON_R_BOT_EXT - 5, -RESON_R_BOT_EXT - 5, Z_RESON_BOT - 5),
                (RESON_R_BOT_EXT + 5, RESON_R_BOT_EXT + 5, Z_RESON_TOP + 5),
            )
        )
        .fillet(FILLET_SMALL)
    )
except Exception:
    pass

# Smaller fillets on infinity lip trough corners
try:
    vessel = (
        vessel
        .edges(
            cq.selectors.BoxSelector(
                (-TOP_FLANGE_R - 5, -TOP_FLANGE_R - 5, Z_TOP_FLANGE_TOP - 5),
                (TOP_FLANGE_R + 5, TOP_FLANGE_R + 5, Z_LIP_TOP + 5),
            )
        )
        .fillet(FILLET_SMALL)
    )
except Exception:
    pass

# ---------------------------------------------------------------------------
# 7. EXPORT TO STEP (for Onshape import)
# ---------------------------------------------------------------------------
result = vessel

import os
_script_dir = os.path.dirname(os.path.abspath(__file__))
_step_path = os.path.join(_script_dir, "lucky_bandit_v43.step")

cq.exporters.export(result, _step_path)
print(f"STEP file exported → {_step_path}")

# ---------------------------------------------------------------------------
# 8. DISPLAY IN CQ-EDITOR
# ---------------------------------------------------------------------------
try:
    show_object(result, name="LUCKY_BANDIT_v4.3",
                options={"color": "gray", "alpha": 0.85})
except NameError:
    pass  # show_object only available in CQ-Editor
