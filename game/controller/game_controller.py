from math import atan2, cos, sin
import math

import pygame
from pygame.locals import (K_1, K_2, K_3, K_4, K_ESCAPE, KEYDOWN,
                           MOUSEBUTTONUP, QUIT)


class GameController():
    
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.meters_to_pixels = self.view.screen.get_width() / self.model.world_width
        
    def compute_trajectory(self, speed: float) -> tuple:
        """
        A handy method for computing the path of a projectile in components
        of speed as pixels.
        
        :param speed: the speed of the projectile in meters per second.
        :return: the trajectory of the projectile in xy components of pixels/frame
        """
        dx = pygame.mouse.get_pos()[0] - self.view.player.rect.centerx
        dy = pygame.mouse.get_pos()[1] - self.view.player.rect.centery
        radians = atan2(dy, dx)
        velocityx = (speed * cos(radians) * self.meters_to_pixels) / self.view.fps
        velocityy = (speed * sin(radians) * self.meters_to_pixels) / self.view.fps
        return (velocityx, velocityy)
        
    def generate_modifiers(self):
        current_spell = self.model.palette[self.model.current_spell_index]
        return {
            'trajectory_in_pixels_per_frame': self.compute_trajectory(current_spell.speed()),
            'radius_in_pixels': math.ceil(current_spell.radius() * self.meters_to_pixels),
            'distance_in_pixels': math.ceil(current_spell.distance() * self.meters_to_pixels),
            'color_in_rgb': current_spell.element.color
        }

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_1:
                        self.model.current_spell_index = 0
                    if event.key == K_2:
                        self.model.current_spell_index = 1
                    if event.key == K_3:
                        self.model.current_spell_index = 2
                    if event.key == K_4:
                        self.model.current_spell_index = 3
                if event.type == MOUSEBUTTONUP and event.button == 1:
                    self.view.create_projectile(self.generate_modifiers())
                elif event.type == QUIT:
                    running = False

            pressed_keys = pygame.key.get_pressed()
            self.view.player.update(pressed_keys)
            self.view.attacks.update(self.generate_modifiers())
            self.view.palette.update(self.model.palette, self.model.current_spell_index)
            self.view.screen.fill((0, 0, 0))

            for entity in self.view.all_sprites:
                self.view.screen.blit(entity.surf, entity.rect)

            pygame.display.flip()
            self.view.clock.tick(self.view.fps)

        pygame.quit()
