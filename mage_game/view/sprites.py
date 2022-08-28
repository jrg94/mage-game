import pygame
from mage_game.view.camera import CharacterCameraGroup
from pygame import RLEACCEL

from ..model import *


class PlayerSprite(pygame.sprite.Sprite):
    """
    The player sprite class.

    :param position: the initial position of the player
    :param source: the player data reference
    """

    def __init__(self, position: tuple, size: tuple, source: Character, camera_group: CharacterCameraGroup):
        super().__init__()
        self.size = size
        self.camera_group = camera_group
        self.sprites = [pygame.image.load(f'assets/player{i}.png') for i in range(1, 3)]
        self.image = pygame.transform.scale(self.sprites[0], self.size)
        self.image.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.image.get_rect(center=position)
        self.source = source
        self.frame = 0

    def move(self, fps: int, meters_to_pixels: float) -> None:
        """
        Moves the character based on key presses.

        :param fps: frames per second
        :param meters_to_pixels: the meters per pixel conversion rate
        """
        keys = pygame.key.get_pressed()
        movement = (self.source._speed * meters_to_pixels) / fps
        if keys[pygame.K_w]:
            self.rect.centery -= movement
        if keys[pygame.K_a]:
            self.rect.centerx -= movement
        if keys[pygame.K_s]:
            self.rect.centery += movement
        if keys[pygame.K_d]:
            self.rect.centerx += movement

    def update(self):
        self.frame += .1
        if self.frame >= len(self.sprites):
            self.frame = 0
        self.image = pygame.transform.scale(
            self.sprites[int(self.frame)], 
            self.size
        )
        if pygame.mouse.get_pos()[0] < (self.rect.center[0] - self.camera_group.offset[0]):
            self.image = pygame.transform.flip(self.image, True, False)


class DummySprite(pygame.sprite.Sprite):
    """
    A dummy enemy used for testing. Does not move or attack.

    :param position: the initial position of the sprite
    :param source: the reference data for the sprite
    """

    def __init__(self, position: tuple, source: Enemy):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((123, 0, 123))
        self.rect = self.image.get_rect(center=position)
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
            self.image.fill((123, 0, 123))
            damage = self.smallfont.render(
                str(self.last_hit), 
                True, 
                (255, 0, 0)
            )
            text_surface = pygame.Surface((50, 50))
            text_surface.fill((255, 0, 0))
            text_surface.set_colorkey((255, 0, 0), RLEACCEL)
            text_surface.blit(
                damage, 
                damage.get_rect(center=text_surface.get_rect().center)
            )
            text_surface.set_alpha(self.alpha)
            self.image.blit(
                text_surface, 
                text_surface.get_rect(center=self.image.get_rect().center)
            )
            self.alpha //= 1.1


class ProjectileSprite(pygame.sprite.Sprite):
    """
    A generic projectile sprite class that can be used to 
    create different types of projectiles.

    :param origin: the reference sprite for the projectile
    :param size: the size of the projectile in xy pixels
    :param source: the reference data for the projectile
    :param camera_group: the camera group that this projectile belongs to
    """

    def __init__(self, origin: pygame.sprite.Sprite, size: tuple, source: Projectile, camera_group: CharacterCameraGroup):
        super().__init__()

        # Storing inputs
        self.source = source
        self.size = size
        self.origin = origin
        self.camera_group = camera_group

        # Generating key sprite attributes
        self.image = pygame.Surface(size)
        self.image.fill((255, 255, 255))
        self.image.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.image.get_rect(center=origin.rect.center)

        # Frame calculations
        self.charge_frames = 0
        self.cast_frames = 0
        self.speed = 0
        self.trajectory = None
        self.position = None
        self.radius = 0
        self.radius_per_frame = 0

        # Collision variables
        self.hit = []

    def cast(self, charge_frames: int, cast_frames: int, speed: int, radius: int):
        """
        Launches the projectile.

        :param charge_frames: the number of frames to spend channeling the attack
        :param cast_frames: the number of frames the spell will spend flying
        :param speed: the speed at which the spell will move across the screen in pixels/frame
        :param radius: the radius of the spell in pixels
        """
        pygame.draw.circle(
            self.image, 
            self.source.element().color, 
            self.image.get_rect().center, 
            1
        )
        self.charge_frames = charge_frames
        self.cast_frames = cast_frames
        self.speed = speed
        self.radius_per_frame = radius / self.cast_frames

    def update(self):
        """
        Animates the projectile. 
        """
        if self.charge_frames > 0:
            self._charge_animation()
        elif self.cast_frames > 0:
            self._shoot()
        elif self.cast_frames == 0:
            self.kill()

    def _charge_animation(self):
        """
        Runs the spell charge animation.
        """
        self._position_projectile()
        self._draw_projectile()
        self.charge_frames -= 1
        self.radius += self.radius_per_frame

    def _shoot(self):
        """
        Runs the spell launching animation.
        """
        self.cast_frames -= 1
        if not self.trajectory:
            self.trajectory = self._compute_trajectory()
        self.position += self.trajectory
        self.rect.centerx = self.position[0]
        self.rect.centery = self.position[1]
        self._draw_projectile()

    def _draw_projectile(self) -> None:
        """
        Draws the projectile spell.
        """
        self.image.fill((255, 255, 255))
        pygame.draw.circle(
            self.image,
            self.source.element().color,
            self.image.get_rect().center,
            self.radius
        )

    def _position_projectile(self) -> None:
        """
        Positions the projectile away from the player. 
        """
        dx = pygame.mouse.get_pos()[0] - (self.origin.rect.centerx - self.camera_group.offset[0])
        dy = pygame.mouse.get_pos()[1] - (self.origin.rect.centery - self.camera_group.offset[1])
        radians = math.atan2(dy, dx)
        x = self.origin.image.get_width() * math.cos(radians) + self.origin.rect.centerx
        y = self.origin.image.get_width() * math.sin(radians) + self.origin.rect.centery
        self.position = pygame.math.Vector2((x, y))
        self.rect.centerx = self.position[0]
        self.rect.centery = self.position[1]

    def _compute_trajectory(self) -> pygame.math.Vector2:
        """
        A handy method for computing the path of a projectile in components
        of speed as pixels.

        :return: the trajectory of the projectile in xy components of pixels/frame
        """
        dx = pygame.mouse.get_pos()[0] - (self.origin.rect.centerx - self.camera_group.offset[0])
        dy = pygame.mouse.get_pos()[1] - (self.origin.rect.centery - self.camera_group.offset[1])
        radians = math.atan2(dy, dx)
        velocityx = self.speed * math.cos(radians)
        velocityy = self.speed * math.sin(radians)
        return pygame.math.Vector2(velocityx, velocityy)


class PaletteSprite(pygame.sprite.Sprite):
    """
    The player's palette sprite class.

    :param position: the location of the palette on the screen
    :param source: the palette model for reference
    """

    def __init__(self, position: tuple, source: Palette):
        super().__init__()
        self.image = pygame.Surface((200, 50))
        self.rect = self.image.get_rect(topleft=position)
        self.source: Palette = source

    def update(self):
        left = 0
        self.image.fill((0, 0, 0))
        active_spell = self.source.get_active_item().get_spell()
        for i, item in enumerate(self.source.get_items()):
            # Draw green square for active item
            if i == self.source.get_active_item_index():
                pygame.draw.rect(
                    self.image,
                    (0, 255, 0),
                    (left, 0, 50, 50),
                    width=2
                )
            # Draw white square otherwise
            else:
                pygame.draw.rect(
                    self.image,
                    (255, 255, 255),
                    (left, 0, 50, 50),
                    width=2
                )
            # Show cast time
            if self.source.get_remaining_casting_time() > 0:
                ratio = self.source.get_remaining_casting_time(
                ) / (active_spell.get_attribute(SpellAttribute.CAST_TIME) * 1000)
                pygame.draw.rect(
                    self.image,
                    (155, 155, 155, 100),
                    (left + 2, 2, 46, 46 * ratio)
                )
            # Add colored circle to square
            pygame.draw.circle(
                self.image,
                item.get_spell().element().color,
                (left + 25, 25),
                10
            )
            left += 50


class ProgressSprite(pygame.sprite.Sprite):
    """
    A sprite used to render the help menu. Shows details
    of player progress.

    :param position: the initial position of the progress sprite
    :param source: the reference data for generating the progress sprite
    """

    def __init__(self, position: tuple, source: Character):
        super().__init__()
        self.image = pygame.Surface((600, 400))
        self.rect = self.image.get_rect(center=position)
        self.source: Character = source
        self.smallfont = pygame.font.Font(None, 24)

    def update(self):
        self.image.fill((123, 123, 123))
        top = 0
        left = 0
        for spell in self.source._spell_book:
            text = self.smallfont.render(
                f"{spell.element().name} Projectile: ",
                True,
                (255, 255, 255)
            )
            self.image.blit(text, (left, top))
            for tracking in spell._attributes.values():
                top += text.get_height()
                text = self.smallfont.render(
                    f"{tracking.attribute.name.title()}: {tracking.effective_value()} {tracking._units} ({tracking.events_to_next_level()} events left)",
                    True,
                    (255, 255, 255)
                )
                self.image.blit(text, (left + 10, top))
            top += text.get_height()
            if top + len(spell._attributes.values()) * text.get_height() > 400:
                left += 300
                top = 0


class StateText(pygame.sprite.Sprite):
    """
    A generic text sprite. Can be used to render text.

    :param position: the initial position of the text
    :param font: the font used to render the text
    :param text: the text to render
    """

    def __init__(self, position: tuple, font: pygame.font.Font, text: str, anchor: str = "topleft") -> None:
        super().__init__()
        self.font = font
        self.image = self.font.render(text, True, (0, 255, 0))
        self.rect = self.image.get_rect(**{anchor: position})
