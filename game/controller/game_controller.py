from math import atan2, cos, sin

import pygame
from pygame.locals import (K_1, K_2, K_3, K_4, K_ESCAPE, KEYDOWN,
                           MOUSEBUTTONUP, QUIT)


class GameController():
    def __init__(self, model, view):
        self.model = model
        self.view = view
        
    def generate_modifiers(self):
        current_spell = self.model.palette[self.model.current_spell_index]
        
        # Calculate trajectory
        speed = current_spell.speed_level * 10
        dx = pygame.mouse.get_pos()[0] - self.view.player.rect.centerx
        dy = pygame.mouse.get_pos()[1] - self.view.player.rect.centery
        radians = atan2(dy, dx)
        velocityx = speed * cos(radians)
        velocityy = speed * sin(radians)
        
        return {
            'trajectory_in_pixels': (velocityx, velocityy),
            'radius_in_pixels': current_spell.radius_level * 5,
            'life_in_frames': current_spell.distance_level * 15,
            'color_in_rgb': current_spell.element.color
        }

    def run(self):
        current_modifiers = {}
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
                    current_modifiers = self.generate_modifiers()
                    self.view.create_projectile(current_modifiers)
                elif event.type == QUIT:
                    running = False

            pressed_keys = pygame.key.get_pressed()
            self.view.player.update(pressed_keys)
            self.view.attacks.update(current_modifiers)
            self.view.palette.update(self.model.palette, self.model.current_spell_index)
            self.view.screen.fill((0, 0, 0))

            for entity in self.view.all_sprites:
                self.view.screen.blit(entity.surf, entity.rect)

            pygame.display.flip()
            self.view.clock.tick(30)

        pygame.quit()
