#!/usr/bin/env python3
"""Add the Latin-1 Supplement accented letters to Barony's pixel_maz fonts.

The pixel_maz font family ships without Latin diacritics, so accented
characters render as the .notdef box in books and UI, breaking every
localization that uses them (PT, ES, FR, DE, IT, Nordic...). This composes the
missing glyphs from existing base letters plus pixel-drawn diacritic marks,
deriving the pixel grid from each font's own geometry.

Covers every composable letter in U+00C0..U+00FF. Letters that are not a
base+mark composition (Æ æ Ð ð Ø ø Þ þ ß) are intentionally skipped.
"""
import os, sys
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

# mark -> the accented letters that use it (base letter is derived by stripping
# the diacritic). Covers every composable letter in U+00C0..U+00FF.
TABLE = {
    'grave':     'ÀÈÌÒÙàèìòù',
    'acute':     'ÁÉÍÓÚÝáéíóúý',
    'circ':      'ÂÊÎÔÛâêîôû',
    'tilde':     'ÃÑÕãñõ',
    'diaeresis': 'ÄËÏÖÜŸäëïöüÿ',
    'ring':      'Åå',
    'cedilla':   'Çç',
}
_BASE = {
    'À':'A','Á':'A','Â':'A','Ã':'A','Ä':'A','Å':'A',
    'È':'E','É':'E','Ê':'E','Ë':'E',
    'Ì':'I','Í':'I','Î':'I','Ï':'I',
    'Ò':'O','Ó':'O','Ô':'O','Õ':'O','Ö':'O',
    'Ù':'U','Ú':'U','Û':'U','Ü':'U',
    'Ý':'Y','Ÿ':'Y','Ñ':'N','Ç':'C',
    'à':'a','á':'a','â':'a','ã':'a','ä':'a','å':'a',
    'è':'e','é':'e','ê':'e','ë':'e',
    'ì':'i','í':'i','î':'i','ï':'i',
    'ò':'o','ó':'o','ô':'o','õ':'o','ö':'o',
    'ù':'u','ú':'u','û':'u','ü':'u',
    'ý':'y','ÿ':'y','ñ':'n','ç':'c',
}
# codepoint -> (base letter, mark)
COMPOSE = {ord(ch): (_BASE[ch], mark)
           for mark, chars in TABLE.items() for ch in chars}

# Marks drawn as pixel cells (col, row). row 0 = bottom row of the mark.
MARKS_ABOVE = {
    'acute':     [(0, 0), (1, 1)],                  # rising  /
    'grave':     [(0, 1), (1, 0)],                  # falling \
    'circ':      [(0, 0), (1, 1), (2, 0)],          # peak    ^
    'tilde':     [(0, 1), (1, 1), (1, 0), (2, 0)],  # wave    ~
    'diaeresis': [(0, 0), (2, 0)],                  # two dots ¨
    'ring':      [(0, 0), (1, 0), (2, 0),           # hollow ring °
                  (0, 1),         (2, 1),
                  (0, 2), (1, 2), (2, 2)],
}
MARK_CEDILLA = [(1, -1), (0, -2), (1, -2)]          # hook below baseline


def pixel_size(font, glyf, cmap):
    o = glyf[cmap[ord('o')]]
    ys = [y for _, y in o.getCoordinates(glyf)[0]]
    return round(max(ys) / 4)


def base_bbox(glyf, gname):
    coords = glyf[gname].getCoordinates(glyf)[0]
    xs = [x for x, _ in coords]; ys = [y for _, y in coords]
    return min(xs), min(ys), max(xs), max(ys)


def draw_square(pen, x, y, p):
    pen.moveTo((x, y)); pen.lineTo((x + p, y))
    pen.lineTo((x + p, y + p)); pen.lineTo((x, y + p)); pen.closePath()


def build_glyph(glyphSet, glyf, base_gname, mark, p):
    minx, miny, maxx, maxy = base_bbox(glyf, base_gname)
    rec = DecomposingRecordingPen(glyphSet)
    glyphSet[base_gname].draw(rec)
    pen = TTGlyphPen(glyphSet)
    rec.replay(pen)
    cells = MARK_CEDILLA if mark == 'cedilla' else MARKS_ABOVE[mark]
    cols = [c for c, _ in cells]
    mark_w = (max(cols) - min(cols) + 1) * p
    cx = (minx + maxx) / 2
    x0 = round((cx - mark_w / 2) / p) * p - min(cols) * p
    anchor = miny if mark == 'cedilla' else maxy
    for c, r in cells:
        draw_square(pen, x0 + c * p, anchor + r * p, p)
    return pen.glyph()


def patch(path, out_path):
    font = TTFont(path)
    glyf = font['glyf']; hmtx = font['hmtx']
    cmap = font.getBestCmap()
    glyphSet = font.getGlyphSet()
    p = pixel_size(font, glyf, cmap)
    order = font.getGlyphOrder()
    uni_tables = [t for t in font['cmap'].tables if t.isUnicode()]
    added = []
    for cp, (base, mark) in sorted(COMPOSE.items()):
        if cp in cmap:
            continue
        if ord(base) not in cmap:
            print(f'  WARN base {base!r} missing, skip U+{cp:04X}'); continue
        gname = 'uni%04X' % cp
        glyf[gname] = build_glyph(glyphSet, glyf, cmap[ord(base)], mark, p)
        hmtx[gname] = hmtx[cmap[ord(base)]]
        if gname not in order:
            order.append(gname)
        for t in uni_tables:
            t.cmap[cp] = gname
        added.append(chr(cp))
    font.setGlyphOrder(order)
    font.save(out_path)
    print(f'{os.path.basename(path):26} pixel={p:4} added {len(added)}: {"".join(added)}')


if __name__ == '__main__':
    src_dir, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    for name in ['pixel_maz.ttf', 'pixel_maz_large.ttf', 'pixel_maz_multiline.ttf']:
        patch(os.path.join(src_dir, name), os.path.join(out_dir, name))
