import pygame
import pygame.freetype

BG_COLOR = (106, 159, 181)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 0)


def create_surface_with_text(
    text: str,
    font_size: int | float,
    text_rgb: tuple[int, int, int],
    bg_rgb: tuple[int, int, int],
) -> pygame.Surface:
    """Returns a surface with rendered text."""
    font = pygame.freetype.SysFont("Courier", int(font_size), bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()


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
        self.rects = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]

    # properties that vary the image and its rect when the mouse is over the element
    @property
    def image(self) -> pygame.Surface:
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
        surface.blit(self.image, self.rect)
