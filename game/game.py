import pygame
from pygame.locals import K_ESCAPE, KEYDOWN, MOUSEBUTTONUP, QUIT

import graphics


def main():
    pygame.init()

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((
        graphics.SCREEN_WIDTH, 
        graphics.SCREEN_HEIGHT
    ))
    player = graphics.Player()
    attacks = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            if event.type == MOUSEBUTTONUP and event.button == 1:
                fireball = graphics.Projectile(
                    player.rect.copy(), 
                    pygame.mouse.get_pos()
                )
                all_sprites.add(fireball)
                attacks.add(fireball)
            elif event.type == QUIT:
                running = False

        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)
        attacks.update()
        screen.fill((0, 0, 0))

        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == '__main__':
    main()
