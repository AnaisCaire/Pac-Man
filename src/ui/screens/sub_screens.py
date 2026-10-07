from ...scores.model import ScoreEntry
from .bottons import UIElement
from ..gfx import bitmap_font, raster
import pygame
import pathlib

_IMAGES_DIR = pathlib.Path(__file__).parent.parent / "images"
BUTTON_FONT_SIZE = 40
BG_COLOR = (106, 159, 181)
LOGO_MAX_WIDTH = 600
# The bitmap font has no underscore, so the config key is described in words.
EVALUATOR_HELP = (
    "EVALUATOR MODE: SET EVALUATOR MODE TRUE IN CONFIG",
    "F: FREEZE   G: SELECT GHOST   IJKL: MOVE GHOST",
    "C: CLEAR LEVEL",
    "EVALUATOR SCORES ARE NOT SAVED",
)
_HELP_FONT_SCALE = 2
_HELP_LINE_HEIGHT = 22
EXIT_WARNING = "You are going to loose your score"


def _handle_button_click(event: pygame.event.Event,
                         buttons: list[UIElement]) -> str | None:
    """Return the action for the clicked button, if any."""
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for button in buttons:
            if button.rect.collidepoint(event.pos):
                return button.action
    return None


class HighscoreScreen():
    """Display the current Top 10 and return to the main menu."""

    def __init__(self, screen_width: int, screen_height: int):
        cx = screen_width // 2
        by = screen_height - 150
        self.back_btn = UIElement(center_position=(cx, by), text="Back",
                                  font_size=BUTTON_FONT_SIZE, action="back")
        self.scores: list[ScoreEntry] = []

    def set_scores(self, scores: list[ScoreEntry]) -> None:
        """Display the current deterministic Top 10 board."""
        self.scores = scores

    def handle_event(self, event: pygame.event.Event) -> str | None:
        return _handle_button_click(event, [self.back_btn])

    def update(self, mouse_pos: tuple[int, int]) -> None:
        self.back_btn.update(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        for index, score in enumerate(self.scores):
            text = bitmap_font.render_text(
                f"{index + 1}: {score.name} {score.score}", 3, (255, 255, 255)
            )
            raster.blit_to_surface(surface, text, (80, 50 + index * 35))
        self.back_btn.draw(surface)


class InstructionsScreen():
    """Show the controls image and a return button."""

    def __init__(self, screen_width: int, screen_height: int):
        cx = screen_width // 2
        by = screen_height - 50
        self.back_btn = UIElement(center_position=(cx, by), text="Back",
                                  font_size=BUTTON_FONT_SIZE, action="back")
        raw_image = raster.load_rgba(str(_IMAGES_DIR / "instructions.png"))
        help_height = len(EVALUATOR_HELP) * _HELP_LINE_HEIGHT
        max_h = by - 40 - help_height
        scale = min(screen_width / raw_image.shape[0], max_h / raw_image.shape[1])
        img_w = int(raw_image.shape[0] * scale)
        img_h = int(raw_image.shape[1] * scale)
        self.image = raster.nearest_neighbor_scale(raw_image, img_w, img_h)
        self.image_rect = pygame.Rect((0, 0), (img_w, img_h))
        self.image_rect.center = (cx, img_h // 2 + 10)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        return _handle_button_click(event, [self.back_btn])

    def update(self, mouse_pos: tuple[int, int]) -> None:
        self.back_btn.update(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        raster.blit_to_surface(surface, self.image, self.image_rect.topleft)
        for index, line in enumerate(EVALUATOR_HELP):
            text = bitmap_font.render_text(line, _HELP_FONT_SCALE, (255, 255, 255))
            raster.blit_to_surface(surface, text, (
                surface.get_width() // 2 - text.shape[0] // 2,
                self.image_rect.bottom + 10 + index * _HELP_LINE_HEIGHT,
            ))
        self.back_btn.draw(surface)


class PauseScreen():
    """Full-screen pause menu with Resume and Return to Main Menu buttons."""

    ACTIONS = {"Resume": "resume", "Return to Menu": "menu"}
    CONFIRM_ACTIONS = {"Keep Playing": "cancel_menu", "Discard Game": "confirm_menu"}

    def __init__(self, screen_width: int, screen_height: int):
        raw_logo = raster.load_rgba(str(_IMAGES_DIR / "main_screen_logo.png"))
        logo_scale = min(LOGO_MAX_WIDTH / raw_logo.shape[0], 1.0)
        logo_w = int(raw_logo.shape[0] * logo_scale)
        logo_h = int(raw_logo.shape[1] * logo_scale)
        self.logo = raster.nearest_neighbor_scale(raw_logo, logo_w, logo_h)
        self.logo_rect = pygame.Rect((0, 0), (logo_w, logo_h))
        self.logo_rect.center = (screen_width // 2, logo_h // 2 + 20)
        self.cx = screen_width // 2
        self.cy = screen_height // 2
        self.confirming_exit = False
        self.buttons: list[UIElement] = []
        self._set_actions(self.ACTIONS)

    def _set_actions(self, actions: dict[str, str]) -> None:
        spacing = BUTTON_FONT_SIZE + 30
        self.buttons = []
        for i, (label, action) in enumerate(actions.items()):
            offset = (i - (len(actions) - 1) / 2) * spacing
            self.buttons.append(UIElement(
                center_position=(self.cx, int(self.cy + offset)), text=label,
                font_size=BUTTON_FONT_SIZE, action=action,
            ))

    def handle_event(self, event: pygame.event.Event) -> str | None:
        action = _handle_button_click(event, self.buttons)
        if action == "menu":
            self.confirming_exit = True
            self._set_actions(self.CONFIRM_ACTIONS)
            return None
        if action == "cancel_menu":
            self.cancel_confirmation()
            return None
        if action == "confirm_menu":
            return "menu"
        return action

    def cancel_confirmation(self) -> None:
        """Restore the standard pause choices without discarding the session."""
        if self.confirming_exit:
            self.confirming_exit = False
            self._set_actions(self.ACTIONS)

    def update(self, mouse_pos: tuple[int, int]) -> None:
        for button in self.buttons:
            button.update(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        raster.blit_to_surface(surface, self.logo, self.logo_rect.topleft)
        if self.confirming_exit:
            warning = bitmap_font.render_text(EXIT_WARNING, 3, (255, 255, 0))
            raster.blit_to_surface(surface, warning, (
                self.cx - warning.shape[0] // 2,
                self.cy - 100,
            ))
        for button in self.buttons:
            button.draw(surface)
