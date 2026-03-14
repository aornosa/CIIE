import pygame

from character_scripts.character import Character, DEFAULT_STATS
from character_scripts.player.inventory import Inventory
from core.audio.audio_listener import AudioListener
from core.audio.audio_manager import AudioManager
from core.collision.layers import LAYERS

DEFAULT_STATS = {
    **DEFAULT_STATS,
    "speed": 200,
    "headshot_chance": 0,
    "headshot_damage": 1.5,
    "defense": 0,
}

class Player(Character):
    def __init__(self, asset, position=(0,0), rotation=0, scale=2.2, name="Player", health=100):
        super().__init__(asset, position, rotation, scale, name, health)
        self.score = 0
        self.inventory = Inventory()
        self.inventory.owner = self
        self.collider.layer = LAYERS["player"]

        self.audio_listener = AudioListener(self)

        self._frame_duration_ms = 100
        self._last_frame_time = pygame.time.get_ticks()
        self._frame_index = 0
        self._anim_state = "idle"
        self._last_position = pygame.Vector2(position)
        self._movement_input = pygame.Vector2(0, 1)
        self._direction_row = 0

        self.animations = self._load_animations_from_sheet(asset)
        self.asset = self.animations["idle"][0][0]

    def _make_background_transparent(self, frame):
        # Remove sheet background color (sampled from top-left pixel) with tolerance.
        bg_r, bg_g, bg_b, _ = frame.get_at((0, 0))
        tolerance = 55
        width, height = frame.get_size()
        for x in range(width):
            for y in range(height):
                r, g, b, a = frame.get_at((x, y))
                if (
                    abs(r - bg_r) <= tolerance
                    and abs(g - bg_g) <= tolerance
                    and abs(b - bg_b) <= tolerance
                ):
                    frame.set_at((x, y), (r, g, b, 0))
        return frame

    def _load_animations_from_sheet(self, sheet_path):
        transparent_color = (255, 0, 255)
        sheet = pygame.image.load(sheet_path).convert_alpha()
        sheet.set_colorkey(transparent_color)

        rows = 6
        total_columns = 16
        state_columns = 8

        frame_width = sheet.get_width() // total_columns
        frame_height = sheet.get_height() // rows

        animations = {"idle": [], "walk": []}

        for row in range(rows):
            idle_row = []
            walk_row = []

            for col in range(state_columns):
                idle_rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                walk_rect = pygame.Rect((col + state_columns) * frame_width, row * frame_height, frame_width, frame_height)

                idle_frame = sheet.subsurface(idle_rect).copy()
                walk_frame = sheet.subsurface(walk_rect).copy()

                idle_frame.set_colorkey(transparent_color)
                walk_frame.set_colorkey(transparent_color)

                idle_frame = self._make_background_transparent(idle_frame)
                walk_frame = self._make_background_transparent(walk_frame)

                idle_row.append(idle_frame)
                walk_row.append(walk_frame)

            animations["idle"].append(idle_row)
            animations["walk"].append(walk_row)

        return animations

    def set_movement_input(self, movement):
        self._movement_input = pygame.Vector2(movement)

    def _get_direction_row(self):
        x = self._movement_input.x
        y = self._movement_input.y

        eps = 1e-5
        if abs(x) <= eps and abs(y) <= eps:
            return self._direction_row

        if x < -eps and y < -eps:
            self._direction_row = 2  # A + W (up-left)
        elif abs(x) <= eps and y < -eps:
            self._direction_row = 3  # W (up)
        elif x > eps and y < -eps:
            self._direction_row = 4  # W + D (up-right)
        elif x < -eps:
            self._direction_row = 1  # A or A + S (left / down-left)
        elif x > eps:
            self._direction_row = 5  # D or S + D (right / down-right)
        else:
            self._direction_row = 0  # S (down)

        return self._direction_row

    def _update_animation_state(self):
        now = pygame.time.get_ticks()
        is_moving = self.position.distance_to(self._last_position) > 0.5
        next_state = "walk" if is_moving else "idle"

        if next_state != self._anim_state:
            self._anim_state = next_state
            self._frame_index = 0
            self._last_frame_time = now

        if now - self._last_frame_time >= self._frame_duration_ms:
            self._frame_index = (self._frame_index + 1) % 8
            self._last_frame_time = now

        self._last_position = pygame.Vector2(self.position)

    def draw(self, surface, camera):
        self._update_animation_state()

        row = self._get_direction_row()
        frame = self.animations[self._anim_state][row][self._frame_index]
        self.asset = frame

        if self.scale != 1:
            width = max(1, int(frame.get_width() * self.scale))
            height = max(1, int(frame.get_height() * self.scale))
            render_frame = pygame.transform.scale(frame, (width, height))
        else:
            render_frame = frame

        screen_pos = self.position - camera.position
        rect = render_frame.get_rect(center=screen_pos)
        surface.blit(render_frame, rect)

    def add_score(self, points):
        self.score += points

    def get_score(self):
        return self.score

    def get_inventory(self):
        return self.inventory
