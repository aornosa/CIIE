import pygame

from core.monolite_behaviour import MonoliteBehaviour

OPACITY = 0.6

class FogOfWar(MonoliteBehaviour):
    def __init__(self, player, camera):
        MonoliteBehaviour.__init__(self)
        self.player = player
        self.camera = camera
        self.angle = 80

        self.arc_template = self.build_arc_points()

        screen = pygame.display.get_surface()
        screen.get_size()

        self.fog_mask = pygame.Surface(screen.get_size(), pygame.SRCALPHA).convert_alpha()
        self.visibility_mask = pygame.Surface(screen.get_size(), pygame.SRCALPHA).convert_alpha()

    def update(self):
        screen = pygame.display.get_surface()
        self.update_vision_mask(1800, 250)
        self.update_visibility_mask(1800, 250)
        screen.blit(self.fog_mask, (0, 0))


    def build_arc_points(self, step=2):
        half = self.angle / 2
        points = []
        for a in range(int(-half - 90), int(half - 90) + 1, step):
            vec = pygame.Vector2(1, 0).rotate(a)
            points.append(vec)
        return points


    def update_vision_mask(self, radius=1800, player_radius=250):
        opacity = int(255 * OPACITY)
        self.fog_mask.fill((0, 0, 0, opacity))

        player_pos = self.player.position - self.camera.position

        # Clear circle around player
        pygame.draw.circle(self.fog_mask, (0, 0, 0, 0), player_pos, player_radius)

        # Starting edge points
        points = [
            player_pos + pygame.Vector2(player_radius, 0).rotate(-self.player.rotation),
            player_pos + pygame.Vector2(-player_radius, 0).rotate(-self.player.rotation)
        ]

        # Rotate precomputed arc instead of recomputing trig
        rot = -self.player.rotation
        for vec in self.arc_template:
            points.append(player_pos + vec.rotate(rot) * radius)

        pygame.draw.polygon(self.fog_mask, (0, 0, 0, 0), points)

    ## Duplicated code. Fix later
    def update_visibility_mask(self, radius=1800, player_radius=250):
        self.visibility_mask.fill((255, 255, 255, 0))

        player_pos = self.player.position - self.camera.position

        # visible circle
        pygame.draw.circle(self.visibility_mask, (255, 255, 255, 255), player_pos, player_radius)

        points = [
            player_pos + pygame.Vector2(player_radius, 0).rotate(-self.player.rotation),
            player_pos + pygame.Vector2(-player_radius, 0).rotate(-self.player.rotation)
        ]

        # Rotate precomputed arc instead of recomputing trig
        rot = -self.player.rotation
        for vec in self.arc_template:
            points.append(player_pos + vec.rotate(rot) * radius)

        pygame.draw.polygon(self.visibility_mask, (255, 255, 255, 255), points)