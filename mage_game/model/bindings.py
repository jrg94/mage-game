import pygame

class Bindings:
    """
    An class for defining key bindings using easy to read names.
    This object should be saved with the game state to preserve user settings.
    I did not want to use pygame in the model, but I'm not sure how
    to record key bindings otherwise. 
    """

    def __init__(self):
        # Game buttons
        self.close_game = [pygame.K_ESCAPE]
        self.select_palette_item = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
        self.move_character = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_w]
        self.cast = [pygame.BUTTON_LEFT]

        # Menu buttons
        self.open_menu = [pygame.K_TAB]
        self.close_menu = [pygame.K_TAB]

        # Help buttons
        self.open_help = [pygame.K_F1]
        self.close_help = [pygame.K_ESCAPE, pygame.K_F1]
