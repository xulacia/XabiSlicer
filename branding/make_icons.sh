#!/bin/bash
# Rasterises branding/xabislicer_icon*.svg into the PNG and ICNS files that replace the
# OrcaSlicer ones in resources/. macOS only (AppKit renders the SVG, iconutil builds the ICNS).
# Run from the repository root after branding/make_branding.py.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMG="$ROOT/resources/images"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# render <svg> <size> <png>: draws the SVG into a transparent bitmap of size x size.
render() {
    osascript -l JavaScript - "$1" "$2" "$3" <<'JXA' >/dev/null
ObjC.import('AppKit');
function run(argv) {
    const src = argv[0], size = parseInt(argv[1], 10), out = argv[2];
    const img = $.NSImage.alloc.initWithContentsOfFile(src);
    if (!img || img.isNil()) throw new Error('cannot read ' + src);
    const rep = $.NSBitmapImageRep.alloc.initWithBitmapDataPlanesPixelsWidePixelsHighBitsPerSampleSamplesPerPixelHasAlphaIsPlanarColorSpaceNameBytesPerRowBitsPerPixel(
        null, size, size, 8, 4, true, false, $.NSDeviceRGBColorSpace, 0, 0);
    rep.size = $.NSMakeSize(size, size);
    $.NSGraphicsContext.saveGraphicsState;
    $.NSGraphicsContext.setCurrentContext($.NSGraphicsContext.graphicsContextWithBitmapImageRep(rep));
    img.drawInRectFromRectOperationFraction($.NSMakeRect(0, 0, size, size), $.NSZeroRect, $.NSCompositingOperationSourceOver, 1.0);
    $.NSGraphicsContext.restoreGraphicsState;
    rep.representationUsingTypeProperties($.NSBitmapImageFileTypePNG, $()).writeToFileAtomically(out, true);
}
JXA
}

ICON="$ROOT/branding/xabislicer_icon.svg"
GRAY="$ROOT/branding/xabislicer_icon_gray.svg"

for spec in "OrcaSlicer-mac_128px.png 128" "OrcaSlicer.png 154" "OrcaSlicerTitle.png 154" \
            "OrcaSlicer_128px.png 128" "OrcaSlicer_154.png 154" "OrcaSlicer_154_title.png 184" \
            "OrcaSlicer_192px.png 192" "OrcaSlicer_192px_transparent.png 192" \
            "OrcaSlicer_32px.png 32" "OrcaSlicer_64.png 64"; do
    set -- $spec
    render "$ICON" "$2" "$IMG/$1"
done
render "$GRAY" 192 "$IMG/OrcaSlicer_192px_grayscale.png"
render "$ICON" 154 "$ROOT/resources/web/image/logo.png"  # welcome page of the setup wizard

# ICNS: the Dock/Finder icon (resources/Icon.icns) and the copy the Info.plist names.
SET="$TMP/icon.iconset"
mkdir -p "$SET"
for s in 16 32 128 256 512; do
    render "$ICON" "$s" "$SET/icon_${s}x${s}.png"
    render "$ICON" "$((s * 2))" "$SET/icon_${s}x${s}@2x.png"
done
iconutil -c icns "$SET" -o "$ROOT/resources/Icon.icns"
cp "$ROOT/resources/Icon.icns" "$IMG/OrcaSlicer.icns"
echo "icons written"
