import pygame

class HitboxDebugger:
    def __init__(self, surface, colour=(255, 0, 0), width=1):
        self.surface = surface
        self.colour = colour  # Red by default
        self.width = width    # Line thickness

    def draw_hitbox(self, game_object):
        # Draw the rect border of the given game object
        rect = game_object.get_rect()
        pygame.draw.rect(self.surface, self.colour, rect, self.width)