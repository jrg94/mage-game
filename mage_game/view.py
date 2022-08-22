import math

import pygame
from pygame.locals import RLEACCEL
from model import SpellAttribute

import model
from eventmanager import *


class GraphicalView(object):
    """
    Draws the model state onto the screen.
    
    :param event_manager: the event manager.
    :param model: the model.
    """

    def __init__(self, event_manager: model.EventManager, model: model.GameEngine):
        self.evManager = event_manager
        event_manager.RegisterListener(self)
        self.model = model
        self.isinitialized = False
        self.fps = None
        self.meters_to_pixels = None
        self.screen = None
        self.clock = None
        self.smallfont = None
        self.player = None
        self.palette = None
        self.attacks = None
        self.all_sprites = None
        self.enemies = None
        self.help = None

    def notify(self, event: Event):
        """
        Receive events posted to the message queue. 
        
        :param event: the event.
        """

        if isinstance(event, InitializeEvent):
            self.initialize()
        elif isinstance(event, QuitEvent):
            # shut down the pygame graphics
            self.isinitialized = False
            pygame.quit()
        elif isinstance(event, TickEvent):
            if not self.isinitialized:
                return
            currentstate = self.model.state.peek()
            if currentstate == model.STATE_MENU:
                self.render_menu()
            if currentstate == model.STATE_PLAY:
                self.render_play()
            if currentstate == model.STATE_HELP:
                self.render_help()
            self.clock.tick(self.fps)
        elif isinstance(event, InputEvent):
            if not self.isinitialized:
                return
            currentstate = self.model.state.peek()
            if currentstate == model.STATE_PLAY:
                if event.click_pos and event.button == "left":
                    self.render_cast(event)
                if event.char and event.char in "1234":
                    self.render_palette(event)

    def _compute_trajectory(self, speed: float, click_position: tuple) -> tuple:
        """
        A handy method for computing the path of a projectile in components
        of speed as pixels.

        :param speed: the speed of the projectile in meters per second.
        :return: the trajectory of the projectile in xy components of pixels/frame
        """
        dx = click_position[0] - self.player.rect.centerx
        dy = click_position[1] - self.player.rect.centery
        radians = math.atan2(dy, dx)
        velocityx = (speed * math.cos(radians) *
                     self.meters_to_pixels) / self.fps
        velocityy = (speed * math.sin(radians) *
                     self.meters_to_pixels) / self.fps
        return (velocityx, velocityy)

    def render_menu(self):
        """
        Render the game menu.
        """
        self.screen.fill((0, 0, 0))
        somewords = self.smallfont.render(
            'You are in the Menu. Space to play. Esc exits.',
            True, (0, 255, 0))
        self.screen.blit(somewords, (0, 0))
        pygame.display.flip()

    def render_play(self):
        """
        Render the game play.
        """

        # Process play game logic
        self.handle_collisions()
        self.model.character.palette.update_cooldowns(self.clock.get_time())
        self.model.character.palette.update_casting_time(self.clock.get_time())
        self.all_sprites.update()

        # Render the scene
        self.screen.fill((0, 0, 0))
        somewords = self.smallfont.render(
            'You are playing the game. F1 for help.',
            True, 
            (0, 255, 0)
        )
        self.screen.blit(
            somewords, 
            (0, self.screen.get_height() - somewords.get_height())
        )
        for entity in self.all_sprites:
            self.screen.blit(entity.surf, entity.rect)
                    
        pygame.display.flip()

    def render_help(self):
        """
        Render the help screen.
        """

        self.screen.fill((0, 0, 0))
        somewords = self.smallfont.render(
            'Help is here. space, escape or return.',
            True, (0, 255, 0))
        self.screen.blit(somewords, (0, 0))
        self.help.update()
        self.screen.blit(self.help.surf, self.help.rect)
        pygame.display.flip()

    def render_cast(self, event: InputEvent):
        """
        Render a spell cast.
        """
        
        if self.model.character.palette.can_cast_active_spell():
            
            self.model.character.palette.reset_casting_time()
        
            # Create projectile sprite
            active_spell = self.model.character.palette.get_active_item().get_spell()
            radius = math.ceil(active_spell.get_attribute_value(SpellAttribute.RADIUS) * self.meters_to_pixels)
            color = active_spell.element().color
            trajectory = self._compute_trajectory(
                active_spell.get_attribute_value(SpellAttribute.SPEED),
                event.click_pos
            )
            projectile = Projectile(
                active_spell,
                trajectory,
                self.player.rect.center,
                self.meters_to_pixels
            )

            # Set starting position
            projectile.rect = projectile.surf.get_rect(center=self.player.rect.center)

            # Draw projectile
            pygame.draw.circle(
                projectile.surf,
                color,
                projectile.surf.get_rect().center,
                radius
            )

            # Add projectile to sprite group
            self.attacks.add(projectile)
            self.all_sprites.add(projectile)

            # Render sprites
            self.all_sprites.update()
            for entity in self.all_sprites:
                self.screen.blit(entity.surf, entity.rect)

            pygame.display.flip()

    def render_palette(self, event: InputEvent):
        """
        Render the palette.
        """
        self.screen.fill((0, 0, 0))
        self.model.character.palette.set_active_palette_item(int(event.char) - 1)
        self.all_sprites.update()
        for entity in self.all_sprites:
            self.screen.blit(entity.surf, entity.rect)
        pygame.display.flip()
        
    def handle_collisions(self):
        for attack in self.attacks:
            enemies: list[pygame.sprite.Sprite] = pygame.sprite.spritecollide(attack, self.enemies, False)
            for enemy in enemies:
                if enemy not in attack.hit:
                    attack.hit.append(enemy)
                    enemy.hit(attack.source.get_attribute_value(SpellAttribute.DAMAGE))
        pygame.display.flip()

    def initialize(self):
        """
        Set up the pygame graphical display and loads graphical resources.
        """

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('Mage Game')
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.fps = 30
        self.meters_to_pixels = self.screen.get_width() / self.model.world_width
        self.smallfont = pygame.font.Font(None, 40)
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.attacks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        
        # Setting up player
        self.player = Player()
        self.player.rect = self.player.surf.get_rect(center=self.screen.get_rect().center)
        self.all_sprites.add(self.player)
        
        # Setting up palette
        self.palette = Palette(self.model.character.palette)
        self.all_sprites.add(self.palette)
        
        # Setting up dummy enemies
        for enemy in self.model.enemies:
            dummy = Dummy(enemy)
            dummy.rect = dummy.surf.get_rect(center=(400, 400))
            self.enemies.add(dummy)
            self.all_sprites.add(dummy)
            
        # Setting up help screen
        self.help = Progress(self.model.character)
        self.help.rect = self.help.surf.get_rect(center=self.screen.get_rect().center)
        
        # Declaring the view initialized
        self.isinitialized = True


class Player(pygame.sprite.Sprite):
    """
    The player sprite class.
    """
    
    def __init__(self):
        super(Player, self).__init__()
        self.sprites = [pygame.image.load(f'assets/player{i}.png') for i in range(1, 3)]
        self.surf = self.sprites[0]
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.current_sprite = 0

    def update(self):
        self.current_sprite += .1
        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0
        self.surf = self.sprites[int(self.current_sprite)]
        
        
class Dummy(pygame.sprite.Sprite):
    
    def __init__(self, source: model.Enemy):
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
            damage = self.smallfont.render(str(self.last_hit), True, (255, 0, 0))
            text_surface = pygame.Surface((50, 50))
            text_surface.fill((255, 0, 0))
            text_surface.set_colorkey((255, 0, 0), RLEACCEL)
            text_surface.blit(damage, damage.get_rect(center=text_surface.get_rect().center))
            text_surface.set_alpha(self.alpha)
            self.surf.blit(text_surface, text_surface.get_rect(center=self.surf.get_rect().center))
            self.alpha //= 1.1


class Projectile(pygame.sprite.Sprite):
    """
    A generic projectile sprite class that can be used to 
    create different types of projectiles.
    """

    def __init__(self, source: model.Projectile, trajectory: tuple, pos: tuple, meters_to_pixels: int):
        super(Projectile, self).__init__()
        self.surf = pygame.Surface((
            source.get_attribute_value(SpellAttribute.RADIUS) * meters_to_pixels * 2, 
            source.get_attribute_value(SpellAttribute.RADIUS) * meters_to_pixels * 2
        ))
        self.surf.fill((255, 255, 255))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(center=pos)
        self.source = source
        self.pos = pygame.Vector2(pos)
        self.trajectory = pygame.Vector2(trajectory)
        self.distance_in_pixels: int = self.source.get_attribute_value(SpellAttribute.DISTANCE) * meters_to_pixels
        self.travel_distance: float = 0
        self.start_time: float = pygame.time.get_ticks()
        self.hit = []

    def update(self):
        """
        Animates the projectile. 
        """
        if pygame.time.get_ticks() - self.start_time > self.source.get_attribute_value(SpellAttribute.CAST_TIME) * 1000:
            self.pos += self.trajectory
            self.travel_distance += math.sqrt(self.trajectory[0] * self.trajectory[0] + self.trajectory[1] * self.trajectory[1])
            self.rect.center = self.pos
            if self.rect.right < 0 or self.travel_distance >= self.distance_in_pixels:
                self.kill()


class Palette(pygame.sprite.Sprite):
    def __init__(self, source: model.Palette):
        super(Palette, self).__init__()
        self.surf = pygame.Surface((200, 50))
        self.rect = self.surf.get_rect()
        self.source: model.Palette = source        

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
                ratio = self.source.get_remaining_casting_time() / (active_spell.get_attribute_value(SpellAttribute.CAST_TIME) * 1000)
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

class Progress(pygame.sprite.Sprite):
    def __init__(self, source: model.Character):
        super().__init__()
        self.surf = pygame.Surface((600, 400))
        self.rect = self.surf.get_rect()
        self.source: model.Character = source  
        self.smallfont = pygame.font.Font(None, 24)   
        
    def update(self):
        self.surf.fill((123, 123, 123))
        top = 0
        left = 0
        for spell in self.source.spell_book:
            text = self.smallfont.render(
                f"{spell.element().name} Projectile: ", 
                True, 
                (255, 255, 255)
            )
            self.surf.blit(text, (left, top))
            for attribute in spell._attributes.values():
                top += text.get_height()
                text = self.smallfont.render(
                    f"{attribute._attribute.name}: {attribute.effective_value()} {attribute._units}", 
                    True, 
                    (255, 255, 255)
                )
                self.surf.blit(text, (left + 10, top))
            top += text.get_height()    
            if top + len(spell._attributes.values()) * text.get_height() > 400:
                left += 300
                top = 0

        