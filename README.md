# barony-pixelmaz-accents

Adds the missing **Latin-1 accented letters** to Barony's `pixel_maz` font
family. The stock fonts have no diacritics, so accented characters render as
`.notdef` boxes in books and UI — breaking every Latin-script localization
(PT, ES, FR, DE, IT, Nordic…).

The script composes each missing glyph from the font's **existing base letter**
plus a pixel-drawn diacritic (acute, grave, circumflex, tilde, diaeresis, ring,
cedilla), snapped to the font's native pixel grid. Advance widths are inherited
from the base letter, so layout is unchanged.

Covers `U+00C0`–`U+00FF` + `Ÿ` (54 glyphs). Non-composable letters
(`Æ æ Ð ð Ø ø Þ þ ß`) are skipped.

## Usage

```sh
pip install fonttools
python3 patch_fonts_full.py <original_fonts_dir> <output_dir>
```

Point `<original_fonts_dir>` at the game's `fonts/` folder (e.g.
`.../steamapps/common/Barony/fonts`). Patched `pixel_maz.ttf`,
`pixel_maz_large.ttf` and `pixel_maz_multiline.ttf` are written to `<output_dir>`.

To use as a Barony mod, drop the patched fonts in your mod's `fonts/` folder —
mods are mounted with priority, so they override the base fonts (restart the
game so the fonts load fresh instead of from cache).

## License

- **This script:** MIT (do as you like).
- **The fonts it modifies** are *not* mine: **"Pixel Maz" © allthatmaz (2008)**,
  licensed **CC BY-NC 3.0**. The script preserves the original `name`-table
  attribution. Any patched font you distribute must keep that attribution, is
  **non-commercial**, and should indicate it was modified.

Written while making a PT-BR book-translation mod; see the upstream report at
TurningWheel/Barony for context.
