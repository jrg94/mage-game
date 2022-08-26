import pygame

class CharacterCameraGroup(pygame.sprite.Group):
    def __init__(self) -> None:
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.half_w = self.screen.get_size()[0] // 2
        self.half_h = self.screen.get_size()[1] // 2
        
    def _center_target_draw(self, target: pygame.sprite.Sprite):
        """
        Centers the camera on a target.

        :param target: a sprite that we want the camera to target
        """
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h
        
    def camera_draw(self, player: pygame.sprite.Sprite):
        """
        A custom drawing method that simulates a camera.

        :param player: the player sprite that we want the camera to target
        """
        
        # Center camera
        self._center_target_draw(player) 
        
        # Draw sprites
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_position = sprite.rect.topleft - self.offset
            self.screen.blit(sprite.image, offset_position)