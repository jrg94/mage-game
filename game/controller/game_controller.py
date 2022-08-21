import pygame
from pygame.locals import (K_1, K_2, K_3, K_4, K_ESCAPE, KEYDOWN,
                           MOUSEBUTTONUP, QUIT, RLEACCEL)


class GameController():
    
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.meters_to_pixels = self.view.screen.get_width() / self.model.world_width
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_1:
                        self.model.palette.current_spell_index = 0
                    if event.key == K_2:
                        self.model.palette.current_spell_index = 1
                    if event.key == K_3:
                        self.model.palette.current_spell_index = 2
                    if event.key == K_4:
                        self.model.palette.current_spell_index = 3
                if event.type == MOUSEBUTTONUP and event.button == 1:
                    if self.model.palette.can_cast_active_spell():
                        self.model.palette.reset_active_spell_cooldown()
                        self.view.create_projectile(self.generate_modifiers())
                elif event.type == QUIT:
                    running = False

            self.model.palette.update_cooldowns(self.view.clock.get_time())

            pressed_keys = pygame.key.get_pressed()
            self.view.player.update(pressed_keys)
            self.view.attacks.update(self.generate_modifiers())
            self.view.palette.update(self.model.palette)
            self.view.screen.fill((0, 0, 0))

            for entity in self.view.all_sprites:
                self.view.screen.blit(entity.surf, entity.rect)

            pygame.display.flip()
            self.view.clock.tick(self.view.fps)

        pygame.quit()
