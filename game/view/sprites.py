import pygame
from pygame.locals import (K_DOWN, K_LEFT, K_RIGHT, K_UP, RLEACCEL, K_a, K_d,
                           K_s, K_w)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("player.png").convert()
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()

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


class Projectile(pygame.sprite.Sprite):
    """
    A generic projectile class that can be used to create different types of projectiles.
    """

    def __init__(self):
        super(Projectile, self).__init__()
        self.surf = pygame.Surface((50, 50))
        self.surf.fill((255, 255, 255))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.total_frames = 0
        self.trajectory = None

    def update(self, modifiers: dict):
        """
        Animates the projectile from a list of modifiers. 
        
        :param modifiers: a dictionary of modifiers for the projectile.
        """
        if not self.trajectory:
            self.trajectory = modifiers.get('trajectory_in_pixels', (10, 10))
        life = modifiers.get('life_in_frames', 15)
        self.total_frames += 1
        self.rect.move_ip(*self.trajectory)
        if self.rect.right < 0 or self.total_frames >= life:
            self.kill()


class Palette(pygame.sprite.Sprite):
    def __init__(self):
        super(Palette, self).__init__()
        self.surf = pygame.Surface((200, 50))
        self.rect = self.surf.get_rect()

    def update(self, palette: list, current_spell_index: int):
        left = 0
        for i, spell in enumerate(palette):
            if i == current_spell_index:
                pygame.draw.rect(self.surf, (0, 255, 0),
                                 (left, 0, 50, 50), width=2)
            else:
                pygame.draw.rect(self.surf, (255, 255, 255),
                                 (left, 0, 50, 50), width=2)
            pygame.draw.circle(
                self.surf, spell.element.color, (left + 25, 25), 10)
            left += 50
