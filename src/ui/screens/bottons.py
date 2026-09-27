import numpy as np
import pygame
from ..gfx import bitmap_font, raster

BG_COLOR = (106, 159, 181)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 0)
_PADDING = 12


def create_surface_with_text(
    text: str,
    font_size: int | float,
    text_rgb: tuple[int, int, int],
    bg_rgb: tuple[int, int, int],
) -> np.ndarray:
    """Returns an RGBA pixel array with the text baked over a solid background."""
    scale = max(1, int(font_size) // 8)
    text_rgba = bitmap_font.render_text(text, scale, text_rgb)
    width = text_rgba.shape[0] + 2 * _PADDING
    height = text_rgba.shape[1] + 2 * _PADDING
    label = np.empty((width, height, 4), dtype=np.uint8)
    label[:, :, 0] = bg_rgb[0]
    label[:, :, 1] = bg_rgb[1]
    label[:, :, 2] = bg_rgb[2]
    label[:, :, 3] = 255
    raster.composite_array(label, text_rgba, _PADDING, _PADDING)
    return label


class UIElement:
    """A single menu button."""

    def __init__(
        self,
        center_position: tuple[int, int],
        text: str,
        font_size: int,
        action: str = "",
    ) -> None:
        self.mouse_over = False
        self.action = action

        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=TEXT_COLOR, bg_rgb=BG_COLOR
        )
        highlighted_image = create_surface_with_text(
            text=text,
            font_size=font_size * 1.2,
            text_rgb=HIGHLIGHT_COLOR,
            bg_rgb=BG_COLOR,
        )

        self.images = [default_image, highlighted_image]
        self.rects: list[pygame.Rect] = []
        for image in self.images:
            rect = pygame.Rect((0, 0), (image.shape[0], image.shape[1]))
            rect.center = center_position
            self.rects.append(rect)

    # properties that vary the image and its rect when the mouse is over the element
    @property
    def image(self) -> np.ndarray:
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self) -> pygame.Rect:
        return self.rects[1] if self.mouse_over else self.rects[0]

    def update(self, mouse_pos: tuple[int, int]) -> None:
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
        else:
            self.mouse_over = False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the element onto a surface."""
        raster.blit_to_surface(surface, self.image, self.rect.topleft)
