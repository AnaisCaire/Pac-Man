"""A built-in 5x7 pixel font, replacing `pygame.freetype` / `pygame.font`.

Neither TrueType shaping nor `Font.render()` has any MLX equivalent — the
closest MLX gets is `mlx_string_put`, a single fixed low-resolution font
with no size/weight control. Rather than depend on an antialiased system
font we cannot defend, text is baked from this glyph table into an RGBA
pixel array, the same primitive an MLX-backed renderer would be limited to.

Only the characters this project's UI actually uses are defined: A-Z,
0-9, space, ':' and '!'. `render_text` upper-cases its input to stay
within that set.
"""

from __future__ import annotations

import numpy as np

_GLYPH_WIDTH = 5
_GLYPH_HEIGHT = 7
_GLYPH_SPACING = 1  # blank columns between characters, in font-pixels

_FONT: dict[str, tuple[str, ...]] = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#...#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ":": (".....", "..#..", ".....", ".....", ".....", "..#..", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
}


def _glyph_mask(char: str) -> np.ndarray:
    """Return the (height, width) boolean pixel mask for a single glyph."""
    rows = _FONT.get(char, _FONT[" "])
    return np.array([[cell == "#" for cell in row] for row in rows], dtype=bool)


def render_text(text: str, scale: int, color: tuple[int, int, int]) -> np.ndarray:
    """Render text to a (width, height, 4) RGBA array using the built-in font.

    Unknown characters render as a blank glyph cell rather than raising, so
    a stray character never crashes a HUD/menu draw call.
    """
    text = text.upper()
    scale = max(1, scale)
    glyph_w = _GLYPH_WIDTH * scale
    glyph_h = _GLYPH_HEIGHT * scale
    spacing = _GLYPH_SPACING * scale
    count = max(1, len(text))
    width = count * glyph_w + (count - 1) * spacing
    rgba = np.zeros((width, glyph_h, 4), dtype=np.uint8)

    x_cursor = 0
    for char in text or " ":
        mask = _glyph_mask(char)
        mask_scaled = np.repeat(np.repeat(mask, scale, axis=0), scale, axis=1)
        mask_wh = mask_scaled.T  # (height, width) -> (width, height)
        cell = rgba[x_cursor:x_cursor + glyph_w]
        cell[:, :, 0] = color[0]
        cell[:, :, 1] = color[1]
        cell[:, :, 2] = color[2]
        cell[:, :, 3] = np.where(mask_wh, 255, 0)
        x_cursor += glyph_w + spacing

    return rgba
