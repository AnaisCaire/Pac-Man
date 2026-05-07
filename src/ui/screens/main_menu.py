import pygame
import pygame.freetype

BG_COLOR = (106, 159, 181)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 0)


def create_surface_with_text(text, font_size, text_rgb, bg_rgb):
    """Returns a surface with rendered text."""
    font = pygame.freetype.SysFont("Courier", int(font_size), bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()


class UIElement():
    """A single menu button."""

    def __init__(self, center_position, text, font_size, action: str = ""):
        self.mouse_over = False
        self.action = action

        default_image = create_surface_with_text(
            text=text, font_size=font_size, text_rgb=TEXT_COLOR, bg_rgb=BG_COLOR
        )
        highlighted_image = create_surface_with_text(
            text=text, font_size=font_size * 1.2, text_rgb=HIGHLIGHT_COLOR, bg_rgb=BG_COLOR
        )

        self.images = [default_image, highlighted_image]
        self.rects = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]
    
    # properties that vary the image and its rect when the mouse is over the element
    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]
    
    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
        else:
            self.mouse_over = False

    def draw(self, surface):
        """ Draws element onto a surface """
        surface.blit(self.image, self.rect)


import pathlib
_IMAGES_DIR = pathlib.Path(__file__).parent.parent / "images"

BUTTON_FONT_SIZE = 40
LOGO_MAX_WIDTH = 600


class MainMenu:
    """Draws the main menu and returns an action string when a button is clicked."""

    # maps button text / action string for game engine
    ACTIONS = {
        "Start Game":      "play",
        "View Highscores": "highscores",
        "Instructions":    "instructions",
        "Exit":            "quit",
    }

    def __init__(self, screen_width: int, screen_height: int):

        # load / scale  logo to fit
        raw_logo = pygame.image.load(str(_IMAGES_DIR / "main_screen_logo.png")).convert_alpha()
        logo_scale = min(LOGO_MAX_WIDTH / raw_logo.get_width(), 1.0)
        logo_w = int(raw_logo.get_width() * logo_scale)
        logo_h = int(raw_logo.get_height() * logo_scale)
        self.logo = pygame.transform.scale(raw_logo, (logo_w, logo_h))
        self.logo_rect = self.logo.get_rect(center=(screen_width // 2, logo_h // 2 + 20))

        # create UIElement for buttons, evenly spaced below the logo
        cx = screen_width // 2
        top = self.logo_rect.bottom + 40
        spacing = BUTTON_FONT_SIZE + 30
        self.buttons = []
        for i, (label, action) in enumerate(self.ACTIONS.items()):
            btn = UIElement(center_position=(cx, top + i * spacing),
                            text=label,
                            font_size=BUTTON_FONT_SIZE,
                            action=action
                            )
            self.buttons.append(btn)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Call once per event. Returns an action string on click, else None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons:
                if button.rect.collidepoint(event.pos):
                    return button.action
        return None

    def update(self, mouse_pos: tuple) -> None:
        for button in self.buttons:
            button.update(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        surface.blit(self.logo, self.logo_rect)
        for button in self.buttons:
            button.draw(surface)