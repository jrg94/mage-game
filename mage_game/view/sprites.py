import pygame
from pygame import RLEACCEL

from ..model import *


class PlayerSprite(pygame.sprite.Sprite):
    """
    The player sprite class.
    """

    def __init__(self):
        super().__init__()
        self.sprites = [pygame.image.load(
            f'assets/player{i}.png') for i in range(1, 3)]
        self.surf = self.sprites[0]
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.current_sprite = 0

    def update(self):
        self.current_sprite += .1
        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0
        self.surf = self.sprites[int(self.current_sprite)]


class DummySprite(pygame.sprite.Sprite):

    def __init__(self, source: Enemy):
        super().__init__()
        self.surf = pygame.Surface((50, 50))
        self.surf.fill((123, 0, 123))
        self.rect = self.surf.get_rect()
        self.source = source
        self.smallfont = pygame.font.Font(None, 40)
        self.last_hit: int | None = None
        self.alpha = 255

    def hit(self, damage: int):
        self.last_hit = damage
        self.alpha = 255
        self.source._hp -= damage
        if self.source._hp <= 0:
            self.kill()

    def update(self):
        if self.last_hit:
            self.surf.fill((123, 0, 123))
            damage = self.smallfont.render(
                str(self.last_hit), True, (255, 0, 0))
            text_surface = pygame.Surface((50, 50))
            text_surface.fill((255, 0, 0))
            text_surface.set_colorkey((255, 0, 0), RLEACCEL)
            text_surface.blit(damage, damage.get_rect(
                center=text_surface.get_rect().center))
            text_surface.set_alpha(self.alpha)
            self.surf.blit(text_surface, text_surface.get_rect(
                center=self.surf.get_rect().center))
            self.alpha //= 1.1


class ProjectileSprite(pygame.sprite.Sprite):
    """
    A generic projectile sprite class that can be used to 
    create different types of projectiles.
    """

    def __init__(self, source: Projectile, trajectory: tuple, pos: tuple, meters_to_pixels: int):
        super().__init__()
        self.surf = pygame.Surface((
            source.get_attribute(SpellAttribute.RADIUS) * meters_to_pixels * 2,
            source.get_attribute(SpellAttribute.RADIUS) * meters_to_pixels * 2
        ))
        self.surf.fill((255, 255, 255))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(center=pos)
        self.source = source
        self.pos = pygame.Vector2(pos)
        self.trajectory = pygame.Vector2(trajectory)
        self.distance_in_pixels: int = self.source.get_attribute(
            SpellAttribute.DISTANCE) * meters_to_pixels
        self.travel_distance: float = 0
        self.start_time: float = pygame.time.get_ticks()
        self.hit = []

    def update(self):
        """
        Animates the projectile. 
        """
        if pygame.time.get_ticks() - self.start_time > self.source.get_attribute(SpellAttribute.CAST_TIME) * 1000:
            self.pos += self.trajectory
            self.travel_distance += math.sqrt(
                self.trajectory[0] * self.trajectory[0] + self.trajectory[1] * self.trajectory[1])
            self.rect.center = self.pos
            if self.rect.right < 0 or self.travel_distance >= self.distance_in_pixels:
                self.kill()


class PaletteSprite(pygame.sprite.Sprite):
    def __init__(self, source: Palette):
        super().__init__()
        self.surf = pygame.Surface((200, 50))
        self.rect = self.surf.get_rect()
        self.source: Palette = source

    def update(self):
        left = 0
        self.surf.fill((0, 0, 0))
        active_spell = self.source.get_active_item().get_spell()
        for i, item in enumerate(self.source.get_items()):
            # Draw green square for active item
            if i == self.source.get_active_item_index():
                pygame.draw.rect(
                    self.surf,
                    (0, 255, 0),
                    (left, 0, 50, 50),
                    width=2
                )
            # Draw white square otherwise
            else:
                pygame.draw.rect(
                    self.surf,
                    (255, 255, 255),
                    (left, 0, 50, 50),
                    width=2
                )
            # Show cast time
            if self.source.get_remaining_casting_time() > 0:
                ratio = self.source.get_remaining_casting_time(
                ) / (active_spell.get_attribute(SpellAttribute.CAST_TIME) * 1000)
                pygame.draw.rect(
                    self.surf,
                    (155, 155, 155, 100),
                    (left + 2, 2, 46, 46 * ratio)
                )
            # Add colored circle to square
            pygame.draw.circle(
                self.surf,
                item.get_spell().element().color,
                (left + 25, 25),
                10
            )
            left += 50


class ProgressSprite(pygame.sprite.Sprite):
    def __init__(self, source: state.Character):
        super().__init__()
        self.surf = pygame.Surface((600, 400))
        self.rect = self.surf.get_rect()
        self.source: state.Character = source
        self.smallfont = pygame.font.Font(None, 24)

    def update(self):
        self.surf.fill((123, 123, 123))
        top = 0
        left = 0
        for spell in self.source._spell_book:
            text = self.smallfont.render(
                f"{spell.element().name} Projectile: ",
                True,
                (255, 255, 255)
            )
            self.surf.blit(text, (left, top))
            for tracking in spell._attributes.values():
                top += text.get_height()
                text = self.smallfont.render(
                    f"{tracking.attribute.name.title()}: {tracking.effective_value()} {tracking._units} ({tracking.events_to_next_level()} events left)",
                    True,
                    (255, 255, 255)
                )
                self.surf.blit(text, (left + 10, top))
            top += text.get_height()
            if top + len(spell._attributes.values()) * text.get_height() > 400:
                left += 300
                top = 0
