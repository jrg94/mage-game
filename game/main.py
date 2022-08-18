import pygame
from pygame.locals import K_ESCAPE, KEYDOWN, MOUSEBUTTONUP, QUIT, K_1, K_2, K_3, K_4

import game_graphics
import game_data


def main():
    pygame.init()

    character = game_data.Character()

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((
        game_graphics.SCREEN_WIDTH, 
        game_graphics.SCREEN_HEIGHT
    ))
    palette = game_graphics.Palette(character)
    player = game_graphics.Player()
    attacks = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(palette)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_1:
                    character.current_spell_index = 0
                if event.key == K_2:
                    character.current_spell_index = 1
                if event.key == K_3:
                    character.current_spell_index = 2
                if event.key == K_4:
                    character.current_spell_index = 3
            if event.type == MOUSEBUTTONUP and event.button == 1:
                attack = game_graphics.Projectile(
                    player.rect.copy(), 
                    pygame.mouse.get_pos(),
                    modifiers=character.generate_modifiers()
                )
                all_sprites.add(attack)
                attacks.add(attack)
            elif event.type == QUIT:
                running = False

        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)
        attacks.update()
        palette.update()
        screen.fill((0, 0, 0))

        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == '__main__':
    main()
