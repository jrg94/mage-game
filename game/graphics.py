from math import atan2, cos, sin

import pygame
from pygame.locals import (K_DOWN, K_LEFT, K_RIGHT, K_UP, RLEACCEL, K_a, K_d,
                           K_s, K_w)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("player.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        )

    # Move the sprite based on user keypresses
    def update(self, pressed_keys):
        if pressed_keys[K_UP] or pressed_keys[K_w]:
            self.rect.move_ip(0, -5)
        if pressed_keys[K_DOWN] or pressed_keys[K_s]:
            self.rect.move_ip(0, 5)
        if pressed_keys[K_LEFT] or pressed_keys[K_a]:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT] or pressed_keys[K_d]:
            self.rect.move_ip(5, 0)

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


class Projectile(pygame.sprite.Sprite):
    """
    A generic projectile class that can be used to create different types of projectiles.

    :param position: the position of the projectile
    :param target: tuple of (x, y) coordinates indicating the target location
    :param modifiers: a dictionary of modifiers to apply to the projectile
    """

    def __init__(self, position: pygame.Rect, target: tuple, modifiers: dict = {}):
        super(Projectile, self).__init__()

        # Initialize the surface
        self.surf = pygame.Surface((50, 50))
        self.surf.fill((255, 255, 255))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)

        # Set required attributes
        self.rect = self.surf.get_rect(center=position.center)
        self.target = target

        # Set optional attributes
        self.speed = modifiers.get('speed', 10)
        self.radius = modifiers.get('radius', 5)
        self.color = modifiers.get('color', (255, 0, 0))
        self.life_in_frames = modifiers.get('life_in_frames', 15)

        # Compute attributes
        self.trajectory = self.calc_trajectory()
        self.total_frames = 0

        # Draw the fireball
        pygame.draw.circle(
            self.surf,
            self.color,
            self.surf.get_rect().center,
            self.radius
        )

    def calc_trajectory(self):
        dx = self.target[0] - self.rect.centerx
        dy = self.target[1] - self.rect.centery
        radians = atan2(dy, dx)
        velocityx = self.speed * cos(radians)
        velocityy = self.speed * sin(radians)
        return velocityx, velocityy

    def update(self):
        self.total_frames += 1
        self.rect.move_ip(*self.trajectory)
        if self.rect.right < 0 or self.total_frames >= self.life_in_frames:
            self.kill()
