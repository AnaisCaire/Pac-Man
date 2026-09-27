"""Pixel-buffer scaling and alpha compositing with no Pygame convenience calls.

Arrays here use Pygame's native (width, height, channels) pixel layout, the
same shape `pygame.surfarray` reads and writes, to avoid transposing on every
call. This replaces `pygame.transform.scale` and the alpha blending that
`Surface.convert_alpha()` + `Surface.blit()` normally do implicitly, since
classic MLX has no equivalent for either: MLX only exposes a raw pixel
buffer (`mlx_get_data_addr`) and `mlx_put_image_to_window`, with no resize
or blend step of its own.
"""

from __future__ import annotations

import numpy as np
import pygame


def load_rgba(path: str) -> np.ndarray:
    """Load an image as a (width, height, 4) uint8 RGBA array.

    Deliberately does not call `.convert_alpha()`: we only need the raw
    pixel data pygame's PNG/XPM loader already decoded, not its blit-time
    blending behaviour.
    """
    surface = pygame.image.load(path)
    rgb = pygame.surfarray.array3d(surface)
    try:
        alpha = pygame.surfarray.array_alpha(surface)
    except ValueError:
        alpha = np.full(rgb.shape[:2], 255, dtype=np.uint8)
    return np.dstack((rgb, alpha)).astype(np.uint8)


def nearest_neighbor_scale(rgba: np.ndarray, width: int, height: int) -> np.ndarray:
    """Resize a (W, H, 4) RGBA array to (width, height, 4).

    Nearest-neighbor sampling via index arrays — no `pygame.transform.scale`
    call, since MLX has no resize function to mirror at all.
    """
    if width <= 0 or height <= 0:
        return np.zeros((max(width, 0), max(height, 0), 4), dtype=np.uint8)
    src_w, src_h = rgba.shape[0], rgba.shape[1]
    col_idx = np.clip((np.arange(width) * src_w) // width, 0, src_w - 1)
    row_idx = np.clip((np.arange(height) * src_h) // height, 0, src_h - 1)
    scaled: np.ndarray = rgba[col_idx][:, row_idx]
    return scaled


def composite_array(dest: np.ndarray, src: np.ndarray, x: int, y: int) -> None:
    """Alpha-blend a (W, H, 4) RGBA array onto another, in place, clipped.

    Used to build static composite images (e.g. a button label baked onto
    its background) once, outside the render loop.
    """
    dest_w, dest_h = dest.shape[0], dest.shape[1]
    src_w, src_h = src.shape[0], src.shape[1]
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + src_w, dest_w), min(y + src_h, dest_h)
    if x0 >= x1 or y0 >= y1:
        return

    sub = src[x0 - x:x1 - x, y0 - y:y1 - y]
    alpha = sub[:, :, 3:4].astype(np.float32) / 255.0
    dest_region = dest[x0:x1, y0:y1]
    dest_rgb = dest_region[:, :, :3].astype(np.float32)
    src_rgb = sub[:, :, :3].astype(np.float32)
    blended_rgb = src_rgb * alpha + dest_rgb * (1.0 - alpha)
    dest_alpha = dest_region[:, :, 3].astype(np.float32)
    src_alpha = sub[:, :, 3].astype(np.float32)
    blended_alpha = src_alpha + dest_alpha * (1.0 - alpha[:, :, 0])

    dest[x0:x1, y0:y1, :3] = blended_rgb.astype(np.uint8)
    dest[x0:x1, y0:y1, 3] = np.clip(blended_alpha, 0, 255).astype(np.uint8)


def blit_to_surface(surface: pygame.Surface, src: np.ndarray,
                    pos: tuple[int, int]) -> None:
    """Alpha-composite a (W, H, 4) RGBA array onto an opaque pygame Surface.

    Only touches the clipped destination region via `pygame.surfarray`'s
    direct pixel-buffer view, so per-frame cost stays proportional to the
    sprite size, not the whole screen.
    """
    x, y = pos
    dest_w, dest_h = surface.get_size()
    src_w, src_h = src.shape[0], src.shape[1]
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + src_w, dest_w), min(y + src_h, dest_h)
    if x0 >= x1 or y0 >= y1:
        return

    sub = src[x0 - x:x1 - x, y0 - y:y1 - y]
    alpha = sub[:, :, 3:4].astype(np.float32) / 255.0
    src_rgb = sub[:, :, :3].astype(np.float32)

    dest_pixels = pygame.surfarray.pixels3d(surface)
    region = dest_pixels[x0:x1, y0:y1].astype(np.float32)
    blended = src_rgb * alpha + region * (1.0 - alpha)
    dest_pixels[x0:x1, y0:y1] = blended.astype(np.uint8)
    del dest_pixels
