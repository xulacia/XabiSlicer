#!/usr/bin/env python3
"""Generates the Xabislicer logo SVGs that replace the OrcaSlicer ones in resources/images.

The app renders its SVGs with nanosvg, which has no text or clip-path support, so the
wordmark is drawn with strokes and the "layer gaps" in the X are lines painted with the
background gradient. Run from the repository root:  python3 branding/make_branding.py
PNG and ICNS files are produced afterwards by branding/make_icons.sh (macOS only).
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "resources", "images")

TEAL, BLUE = "#14B8A6", "#2563EB"
GRAY_A, GRAY_B = "#9CA3AF", "#4B5563"

# --- the mark, in a 1024 x 1024 box -------------------------------------------------------

LAYER_YS = [352, 416, 480, 544, 608, 672]


def mark(c1, c2, background):
    """background: 'square', 'circle' or None (white X on transparent is not used; None draws a
    gradient X with no background)."""
    grad = (f'<linearGradient id="g" x1="0" y1="0" x2="1024" y2="1024" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>')
    parts = [f"<defs>{grad}</defs>"]
    if background == "square":
        parts.append('<rect x="0" y="0" width="1024" height="1024" rx="224" ry="224" fill="url(#g)"/>')
    elif background == "circle":
        parts.append('<circle cx="512" cy="512" r="512" fill="url(#g)"/>')
    ink = "#FFFFFF" if background else "url(#g)"
    gap = "url(#g)" if background else "#FFFFFF"
    parts.append(f'<path d="M300 288 L724 736 M724 288 L300 736" stroke="{ink}" stroke-width="128" '
                 f'stroke-linecap="round" fill="none"/>')
    if background:  # layer gaps only read well on a filled background
        for y in LAYER_YS:
            parts.append(f'<path d="M200 {y} L824 {y}" stroke="{gap}" stroke-width="16" fill="none"/>')
    parts.append(f'<rect x="280" y="808" width="464" height="36" rx="18" ry="18" fill="{ink}" '
                 f'fill-opacity="0.9"/>')
    return "".join(parts)


def svg(w, h, view, body):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{w}" height="{h}" viewBox="{view}">{body}</svg>\n')


# --- stroked wordmark ----------------------------------------------------------------------

# Glyphs on a grid 14 units tall; (path, advance width).
GLYPHS = {
    "X": ("M0 0 L9 14 M9 0 L0 14", 9),
    "A": ("M0 14 L4.5 0 L9 14 M2 8.5 L7 8.5", 9),
    "B": ("M0 7 L0 0 L5.2 0 Q8.6 0 8.6 3.5 Q8.6 7 5.2 7 L0 7 L0 14 L5.8 14 Q9.2 14 9.2 10.5 Q9.2 7 5.8 7", 9.2),
    "I": ("M0 0 L0 14", 0),
    "S": ("M8.6 2.2 Q7.2 0 4.5 0 Q0.6 0 0.6 3.6 Q0.6 6.6 4.6 7 Q9 7.5 9 10.6 Q9 14 4.6 14 Q1.5 14 0 11.8", 9),
    "L": ("M0 0 L0 14 L8 14", 8),
    "C": ("M9 2.6 Q7.6 0 4.9 0 Q0 0 0 7 Q0 14 4.9 14 Q7.6 14 9 11.4", 9),
    "E": ("M8 0 L0 0 L0 14 L8 14 M0 7 L6.5 7", 8),
    "R": ("M0 14 L0 0 L5.4 0 Q9 0 9 3.6 Q9 7.2 5.4 7.2 L0 7.2 M4.6 7.2 L9 14", 9),
}
SPACING = 3.6


def wordmark(text, x, y, scale, color, stroke=2.3):
    parts, pen = [], 0.0
    for ch in text:
        d, adv = GLYPHS[ch]
        parts.append(f'<path transform="translate({x + pen * scale:.2f} {y:.2f}) scale({scale})" d="{d}" '
                     f'stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" '
                     f'fill="none"/>')
        pen += adv + SPACING
    return "".join(parts), (pen - SPACING) * scale


def lockup(w, h, icon_size, text_scale, text_color):
    pad = (h - icon_size) / 2
    icon = (f'<g transform="translate({pad} {pad}) scale({icon_size / 1024})">'
            f'{mark(TEAL, BLUE, "square")}</g>')
    text, _ = wordmark("XABISLICER", pad * 2 + icon_size, (h - 14 * text_scale) / 2, text_scale, text_color)
    return svg(w, h, f"0 0 {w} {h}", icon + text)


def splash(word_color, sub_color):
    """480 x 480 splash logo. The app draws the version at 72 % and the progress text at 85 %
    of the height, so everything here stays above y = 330."""
    size, top = 142, 70
    icon = (f'<g transform="translate({(480 - size) / 2} {top}) scale({size / 1024})">'
            f'{mark(TEAL, BLUE, "square")}</g>')
    parts = [icon]
    for text, scale, y, color, stroke in (("XABI", 3.7, top + size + 18, word_color, 2.0),
                                          ("SLICER", 2.3, top + size + 82, sub_color, 2.3)):
        width = (sum(GLYPHS[c][1] for c in text) + SPACING * (len(text) - 1)) * scale
        parts.append(wordmark(text, (480 - width) / 2, y, scale, color, stroke)[0])
    return svg(480, 480, "0 0 480 480", "".join(parts))


def main():
    square = mark(TEAL, BLUE, "square")
    files = {
        "OrcaSlicer.svg": svg(64, 64, "0 0 1024 1024", square),
        "OrcaSlicer_gradient.svg": svg(1024, 1024, "0 0 1024 1024", square),
        "OrcaSlicer_gradient_circle.svg": svg(1024, 1024, "0 0 1024 1024", mark(TEAL, BLUE, "circle")),
        "OrcaSlicer_gradient_narrow.svg": svg(1024, 1024, "0 0 1024 1024", mark(TEAL, BLUE, None)),
        "OrcaSlicer_gray.svg": svg(1024, 1024, "0 0 1024 1024", mark(GRAY_A, GRAY_B, "square")),
        "OrcaSlicer_horizontal_light.svg": lockup(214, 80, 56, 1.02, "#1F2937"),
        "OrcaSlicer_horizontal_dark.svg": lockup(214, 80, 56, 1.02, "#F9FAFB"),
        "OrcaSlicer_about.svg": lockup(560, 125, 100, 2.55, "#1F2937"),
        "OrcaSlicer_about_dark.svg": lockup(560, 125, 100, 2.55, "#F9FAFB"),
        "splash_logo.svg": splash(TEAL, "#6B7280"),
        "splash_logo_dark.svg": splash("#2DD4BF", "#D1D5DB"),
    }
    for name, content in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(content)
    # Master icon for the PNG/ICNS step.
    with open(os.path.join(os.path.dirname(__file__), "xabislicer_icon.svg"), "w", encoding="utf-8") as f:
        f.write(svg(1024, 1024, "0 0 1024 1024", square))
    with open(os.path.join(os.path.dirname(__file__), "xabislicer_icon_gray.svg"), "w", encoding="utf-8") as f:
        f.write(svg(1024, 1024, "0 0 1024 1024", mark(GRAY_A, GRAY_B, "square")))
    print("wrote", len(files) + 2, "SVG files")


if __name__ == "__main__":
    main()
