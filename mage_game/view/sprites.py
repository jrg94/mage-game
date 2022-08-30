import logging
import random

import pygame
from mage_game.view.camera import CharacterCameraGroup
from pygame import RLEACCEL

from ..model import *

logger = logging.getLogger(__name__)


class PlayerSprite(pygame.sprite.Sprite):
    """
    The player sprite class.

    :param tuple position: the initial position of the player
    :param tuple size: the size of the sprite
    :param Character source: the player data reference
    :param CharacterCameraGroup camera_group: the set of sprites rendered from the POV of the player
    """

    def __init__(self, position: tuple, size: tuple, source: Character, camera_group: CharacterCameraGroup) -> None:
        logger.debug(f"Created player sprite on screen at {position} with dimensions {size}.")
        super().__init__()
        self.size = size
        self.camera_group = camera_group
        self.sprites = [pygame.image.load(f'assets/player{i}.png') for i in range(1, 3)]
        self.image = pygame.transform.scale(self.sprites[0], self.size)
        self.image.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.image.get_rect(center=position)
        self.source = source
        self.frame = 0
        self.fps = 0
        self.meters_to_pixels = 0
        self.position = pygame.math.Vector2(position)
        
    def prepare_player(self, fps: int, meters_to_pixels: float) -> None:
        """
        To avoid overloading the initialization of the player sprite,
        I added this method to allow additional variables to be passed
        to the sprite. 

        :param fps: the number of frames per second
        :param meters_to_pixels: the number of meters per frame
        """
        self.fps = fps
        self.meters_to_pixels = meters_to_pixels

    def _move(self) -> None:
        """
        Moves the character based on key presses.

        :param int fps: frames per second
        :param float meters_to_pixels: the meters per pixel conversion rate
        """
        keys = pygame.key.get_pressed()
        movement = self.source._speed / self.fps
        if keys[pygame.K_w]:
            self.source.move_entity(0, -movement)
        if keys[pygame.K_a]:
            self.source.move_entity(-movement, 0)
        if keys[pygame.K_s]:
            self.source.move_entity(0, movement)
        if keys[pygame.K_d]:
            self.source.move_entity(movement, 0)
        self.position = pygame.math.Vector2(
            self.source.coordinates.x * self.meters_to_pixels,
            self.source.coordinates.y * self.meters_to_pixels
        )
        self.rect.centerx = self.position[0]
        self.rect.centery = self.position[1]

    def update(self) -> None:
        """
        Updates the player sprite on each frame.
        """
        self._move()
        self.frame += .1
        if self.frame >= len(self.sprites):
            self.frame = 0
        self.image = pygame.transform.scale(
            self.sprites[int(self.frame)], 
            self.size
        )
        if pygame.mouse.get_pos()[0] < (self.position[0] - self.camera_group.offset[0]):
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

    def hit(self, damage: int) -> None:
        """
        Registers a hit of the DummySprite. 

        :param damage: the amount of damage to remove from the DummySprite.
        """
        self.last_hit = damage
        self.alpha = 255
        self.source._hp -= damage
        if self.source._hp <= 0:
            self.kill()

    def update(self):
        """
        Updates the DummySprite every frame.
        """
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
    :param enemy_group: the group of enemies that could be hit
    """

    def __init__(
            self, 
            origin: pygame.sprite.Sprite, 
            size: tuple, 
            source: Projectile, 
            camera_group: CharacterCameraGroup, 
            enemy_group: CharacterCameraGroup
        ):
        super().__init__()

        # Storing inputs
        self.source = source
        self.size = size
        self.origin = origin
        self.camera_group = camera_group
        self.enemy_group = enemy_group

        # Generating key sprite attributes
        self.image = pygame.Surface(size)
        self.image.fill((255, 255, 255))
        self.image.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.image.get_rect()

        # Frame calculations
        self.charge_frames = 0
        self.cast_frames = 0
        self.speed = 0
        self.trajectory = None
        self.position = None
        self.radius = 1
        self.radius_per_frame = 0

        # Collision variables
        self.sprites_hit = []

    def cast(self, charge_frames: int, cast_frames: int, speed: int, radius: int) -> None:
        """
        Launches the projectile.

        :param charge_frames: the number of frames to spend channeling the attack
        :param cast_frames: the number of frames the spell will spend flying
        :param speed: the speed at which the spell will move across the screen in pixels/frame
        :param radius: the radius of the spell in pixels
        """
        self.charge_frames = charge_frames
        self.cast_frames = cast_frames
        self.speed = speed
        self.radius_per_frame = radius / self.cast_frames
        self._position_projectile()
        self._draw_projectile()

    def update(self) -> None:
        """
        Animates the projectile. 
        """
        if self.charge_frames > 0:
            self._charge_animation()
        elif self.cast_frames > 0:
            self._shoot_animation()
            self._compute_collisions()
        elif self.cast_frames == 0:
            self.kill()

    def _charge_animation(self) -> None:
        """
        Runs the spell charge animation.
        """
        self._draw_projectile()
        self._trajectory_animation()
        self._position_projectile()
        self.charge_frames -= 1
        self.radius += self.radius_per_frame

    def _shoot_animation(self) -> None:
        """
        Runs the spell launching animation.
        """
        if not self.trajectory:
            self.trajectory = self._compute_trajectory()
        self.position += self.trajectory
        self.rect.centerx = self.position[0]
        self.rect.centery = self.position[1]
        self._draw_projectile()
        self._particle_animation()
        self.cast_frames -= 1
        
    def _trajectory_animation(self) -> None:
        """
        Draws a line between the projectile and the mouse.
        """
        pygame.draw.aaline(
            pygame.display.get_surface(), 
            self.source.element().color, 
            pygame.mouse.get_pos(),
            self.position - self.camera_group.offset, 
        )
        
    def _particle_animation(self) -> None:
        """
        Adds a nice particle effect to the spells.
        """
        particle_count = (self.size[0] * self.size[1]) // 20
        particle_color = self._get_adjacent_color(self.source.element().color, random.randint(25, 35))
        for _ in range(particle_count):
            x = random.randint(0, self.size[0])
            y = random.randint(0, self.size[1])
            pygame.draw.circle(
                self.image,
                particle_color,
                (x, y),
                1
            )
            
    def _get_adjacent_color(self, rgb: tuple, degrees: int = 30) -> pygame.Color:
        """
        Computes a nearby color (default +30 degrees).

        :param rgb: a color in RGB
        :param degrees: the degrees away out of 360, defaults to 30
        :return: a pygame color object with the color shifted by degrees
        """
        color = pygame.Color(rgb[0], rgb[1], rgb[2])
        h = (color.hsla[0] + degrees) % 360
        color.hsla = (h, color.hsla[1], color.hsla[2], color.hsla[3])
        return color

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
        dx = pygame.mouse.get_pos()[0] - (self.origin.position[0] - self.camera_group.offset[0])
        dy = pygame.mouse.get_pos()[1] - (self.origin.position[1] - self.camera_group.offset[1])
        radians = math.atan2(dy, dx)
        x = self.origin.image.get_width() * math.cos(radians) + self.origin.position[0]
        y = self.origin.image.get_width() * math.sin(radians) + self.origin.position[1]
        self.position = pygame.math.Vector2((x, y))
        self.rect.centerx = self.position[0]
        self.rect.centery = self.position[1]

    def _compute_trajectory(self) -> pygame.math.Vector2:
        """
        A handy method for computing the path of a projectile in components
        of speed as pixels.

        :return: the trajectory of the projectile in xy components of pixels/frame
        """
        dx = pygame.mouse.get_pos()[0] - (self.origin.position[0] - self.camera_group.offset[0])
        dy = pygame.mouse.get_pos()[1] - (self.origin.position[1] - self.camera_group.offset[1])
        radians = math.atan2(dy, dx)
        velocityx = self.speed * math.cos(radians)
        velocityy = self.speed * math.sin(radians)
        return pygame.math.Vector2(velocityx, velocityy)
    
    def _compute_collisions(self):
        """
        Determines if this projectile has hit any of the enemies.
        """
        enemies: list[pygame.sprite.Sprite] = pygame.sprite.spritecollide(
            self, 
            self.enemy_group, 
            False
        )
        for enemy in enemies:
            if enemy not in self.sprites_hit:
                damage: AttributeTracking = self.source.get_tracking(SpellAttribute.DAMAGE)
                damage.trigger_event()
                self.sprites_hit.append(enemy)
                enemy.hit(damage.effective_value())


class PaletteSprite(pygame.sprite.Sprite):
    """
    The player's palette sprite class.

    :param position: the location of the palette on the screen
    :param source: the palette model for reference
    """

    def __init__(self, position: tuple, size: tuple, source: Palette, clock: pygame.time.Clock):
        super().__init__()
        self.size = size
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect(topleft=position)
        self.source: Palette = source
        self.clock: pygame.time.Clock = clock
        self.font = pygame.font.Font(None, 24)
        
    def _manage_timers(self) -> None:
        """
        A helper method that updates the timers in the palette source.
        """
        self.source.update_casting_time(self.clock.get_time())
        self.source.update_cooldowns(self.clock.get_time())

    def _draw_palette_cell(self, cell: int, left: int, line_width: int, color: tuple) -> None:
        """
        A helper method for drawing the palette squares that showcase each 
        cell in the palette.

        :param cell: the index of the cell for labeling purposes
        :param left: the topleft location of the cell
        :param line_width: the thickness of the line for the cell
        :param color: the color of the text and line for the cell
        """
        cell_index_text = self.font.render(str(cell + 1), True, color)
        pygame.draw.rect(
            self.image,
            color,
            (left, 0, self.size[0] / 4, self.size[1]),
            width=line_width,
            border_radius=5
        )
        self.image.blit(cell_index_text, (left + 5, 5))
        
    def _draw_cast_time_animation(self, left: int, line_width: int):
        """
        A helper method that draws the cast time animation on this palette.

        :param left: _description_
        :param line_width: _description_
        """
        cast_time = self.source.get_active_item().get_spell().get_attribute(SpellAttribute.CAST_TIME) * 1000
        remaining_cast_time = self.source.get_remaining_casting_time()
        ratio = remaining_cast_time / cast_time
        pygame.draw.rect(
            self.image,
            (155, 155, 155, 100),
            (
                left + line_width, 
                line_width, 
                self.size[0] / 4 - line_width * 2, 
                (self.size[1] - line_width * 2) * ratio
            )
        )
        
    def _draw_spell_icon(self, left, palette_item: PaletteItem):
        """
        A helper method that draws the spell icon on the palette.

        :param left: the left position of the spell
        :param palette_item: the palette item to draw
        """
        pygame.draw.circle(
            self.image,
            palette_item.get_spell().element().color,
            (left + self.size[0] / 8, self.size[1] / 2),
            self.size[1] / 4
        )
        
    def _draw_palette(self):
        """
        A helper method that draws the current palette.
        """
        left = 0
        line_width = 2
        self.image.fill((0, 0, 0))
        for i, item in enumerate(self.source.get_items()):
            if self.source.get_remaining_casting_time() > 0:
                self._draw_cast_time_animation(left, line_width)
            self._draw_spell_icon(left, item)
            if i == self.source.get_active_item_index():
                self._draw_palette_cell(i, left, line_width, (0, 255, 0))
            else:
                self._draw_palette_cell(i, left, line_width, (255, 255, 255))
            left += self.size[0] / 4

    def update(self):
        """
        The generic update method that occurs each frame.
        """
        self._manage_timers()
        self._draw_palette()
        

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
        
class ButtonSprite(pygame.sprite.Sprite):
    """
    A handy class for making buttons.
    """
    
    def __init__(self, position: tuple, font: pygame.font.Font, text: str, color: tuple | str = "black") -> None:
        super().__init__()
        self.font = font
        self.size_plus_padding = tuple(coord + 10 for coord in self.font.size(text))
        self.image = pygame.Surface(self.size_plus_padding)
        self.image.set_colorkey("white", RLEACCEL)
        self.rect = self.image.get_rect(center=position)
        self.text_surface = self.font.render(text, True, color)
        self.text_rect = self.text_surface.get_rect(center=self.image.get_rect().center)
        
    def detect_press(self, event: MouseEvent) -> bool:
        """
        A handy method for checking if a mouse event has triggered this button. 

        :param event: a mouse event object
        :return: True if this button was pressed; False, otherwise.
        """
        return self.rect.collidepoint(event.click_pos) and event.button == 1
    
    def update(self) -> None:
        self.image.fill((255, 255, 255))
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(self.image, "gray47", self.image.get_rect(), border_radius=8)
        else:
            pygame.draw.rect(self.image, "gray70", self.image.get_rect(), border_radius=8)
        pygame.draw.rect(self.image, "black", self.image.get_rect(), border_radius=8, width=1)
        self.image.blit(self.text_surface, self.text_rect)
