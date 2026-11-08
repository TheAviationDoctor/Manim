from manim import *
import numpy as np

# Configurable styling
BG = "#111821"
COCOA_BASE = "#421B14"
COCOA_DARK = "#37160F"
COCOA_RIM = "#7F432D"
COCOA_FACE = "#AE704A"
COCOA_GLINT = "#CD956B"
CREAM = "#F1E9DB"
GOLD = "#DDA45D"
S = 0.72                         # Manim units per chocolate square
X0, Y0 = -1.44, -2.95         # bottom-left of the original 4 x 8 bar
RISE = 0.25                     # diagonal's rise per 1 horizontal square
Y_CUT = 3.5                    # y-coordinate of diagonal at x=0


def clip_half_plane(poly, axis, bound, keep_positive):
    """Clip a convex polygon against a vertical or horizontal half-plane."""
    if not poly:
        return []
    out = []
    def coord(p):
        return p[axis]
    def inside(p):
        return coord(p) >= bound - 1e-10 if keep_positive else coord(p) <= bound + 1e-10
    for i in range(len(poly)):
        a, b = poly[i - 1], poly[i]
        ia, ib = inside(a), inside(b)
        if ia != ib:
            delta = b[axis] - a[axis]
            t = (bound - a[axis]) / delta if abs(delta) > 1e-12 else 0
            out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
        if ib:
            out.append(b)
    return out


def clipped_rect(poly, x0, y0, x1, y1):
    for axis, bound, pos in [(0, x0, True), (0, x1, False),
                             (1, y0, True), (1, y1, False)]:
        poly = clip_half_plane(poly, axis, bound, pos)
        if not poly:
            return []
    return poly


def area(poly):
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1]
                   - poly[(i + 1) % len(poly)][0] * poly[i][1]
                   for i in range(len(poly))) / 2.0) if len(poly) >= 3 else 0


def world_poly(poly):
    return [np.array([X0 + x * S, Y0 + y * S, 0.0]) for x, y in poly]


def filled_polygon(poly, color):
    if area(poly) < 1e-5:
        return None
    return Polygon(*world_poly(poly), stroke_width=0, fill_color=color,
                   fill_opacity=1)


def chocolate_fragment(footprint):
    """Generate real clipped tile geometry with independently movable, precisely clipped facets."""
    out = VGroup()
    base = filled_polygon(footprint, COCOA_BASE)
    out.add(base)
    for row in range(8):
        for col in range(4):
            # Three nested facets and one top glint per chocolate square.
            # Each facet is clipped to the fragment's exact polygon.
            facets = [
                (col + .045, row + .045, col + .955, row + .955, COCOA_DARK),
                (col + .090, row + .090, col + .910, row + .910, COCOA_RIM),
                (col + .155, row + .158, col + .845, row + .848, COCOA_FACE),
                (col + .185, row + .770, col + .815, row + .813, COCOA_GLINT),
            ]
            for x0, y0, x1, y1, color in facets:
                p = clipped_rect(footprint, x0, y0, x1, y1)
                tile = filled_polygon(p, color)
                if tile is not None:
                    out.add(tile)
    return out


def pt(x, y):
    return np.array([X0 + x * S, Y0 + y * S, 0])


class InfiniteChocolate(Scene):
    def construct(self):
        self.camera.background_color = BG
        full = [(0, 0), (4, 0), (4, 8), (0, 8)]
        bottom = [(0, 0), (4, 0), (4, 4.5), (0, 3.5)]
        square = [(0, 7), (1, 7), (1, 8), (0, 8)]
        original = chocolate_fragment(full)
        C = chocolate_fragment(bottom).set_z_index(2)
        extra = chocolate_fragment(square).set_z_index(3)

        # Construct each upper fragment at its final, perfectly aligned
        # location, then translate it back to its starting location.
        # The integer offsets preserve every facet's grid alignment.
        A = chocolate_fragment([(3, 4.25), (4, 4.5), (4, 8), (3, 8)])
        B = chocolate_fragment([(0, 3.5), (3, 4.25), (3, 8), (0, 8)])
        A.shift(LEFT * 3*S + DOWN * S).set_z_index(1)
        B.shift(RIGHT * S).set_z_index(1)
        A_shape = [m.get_points().copy() for m in A.family_members_with_points()]
        B_shape = [m.get_points().copy() for m in B.family_members_with_points()]

        # Permanent dimension marks give a fixed visual reference.
        ticks = VGroup(Line(pt(4.25, 0), pt(4.48, 0)),
                       Line(pt(4.25, 8), pt(4.48, 8)),
                       Line(pt(4.4, 0), pt(4.4, 8)))
        ticks.set_stroke(CREAM, width=1, opacity=.4)
        eight = Text("8", font_size=20, color=CREAM).move_to(pt(4.8, 4))
        self.add(ticks, eight, original)
        self.wait(.5)

        cuts = VGroup(Line(pt(0, 3.5), pt(4, 4.5)),
                      Line(pt(1, 3.75), pt(1, 8)),
                      Line(pt(0, 7), pt(1, 7)))
        cuts.set_stroke(GOLD, width=3)
        self.play(Create(cuts[0]), run_time=.5)
        self.play(Create(cuts[1]), Create(cuts[2]), run_time=.4)
        # Replace identical geometry instantly; no double-opacity dissolve.
        self.remove(original, cuts, *cuts)
        self.add(B, A, C, extra)

        lift = UP * .48
        self.play(A.animate.shift(lift), B.animate.shift(lift),
                  extra.animate.shift(lift), run_time=.55)
        self.play(extra.animate.move_to(pt(-2.1, 7.35)),
                  run_time=.55)

        # Narrow section passes above the broad section, like the reference.
        self.play(A.animate.shift(UP * .6), run_time=.25)
        self.play(A.animate.shift(RIGHT * 3*S),
                  B.animate.shift(LEFT * S), run_time=.65)

        # Close the gap with rigid translations only. A moves a net one
        # full row upward; B has no net vertical displacement. Neither the
        # chocolate grid nor any fragment outline changes during the move.
        self.play(A.animate.shift(UP * (S - .48 - .6)),
                  B.animate.shift(-lift), run_time=1.15)

        # Check the actual animated geometry: every control point moved by
        # the same offset, so no facet has changed shape or size.
        for fragment, before, offset in (
            (A, A_shape, RIGHT * 3*S + UP * S),
            (B, B_shape, LEFT * S),
        ):
            for member, points in zip(fragment.family_members_with_points(), before):
                assert np.allclose(member.get_points(), points + offset)
        assert np.isclose(A.get_top()[1], pt(0, 8)[1])
        assert np.isclose(B.get_top()[1], pt(0, 8)[1])

        # Consolidate identical visible facets to eliminate raster hairlines
        # at the cut boundary; this does not animate or change any square.
        self.remove(C, A, B)
        self.add(original)
        self.wait(.65)
        self.play(extra.animate.shift(LEFT * (config.frame_width + 2)),
                  run_time=1.0, rate_func=smooth)
        self.remove(extra)
        self.wait(.5)