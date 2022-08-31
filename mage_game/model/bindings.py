class Bindings:
    """
    An class for defining key bindings using easy to read names.
    This object should be saved with the game state to preserve user settings.
    All keyboard keys are stored as strings. Mouse buttons are stored as
    numbers (e.g., M1 = 1, M2 = 2, etc.).
    """

    def __init__(self):
        # Game buttons
        self.close_game = ["escape"]
        self.select_palette_item = ["1", "2", "3", "4"]
        self.move_character = ["a", "s", "d", "w"]
        self.cast = [1]

        # Menu buttons
        self.open_menu = ["tab"]
        self.close_menu = ["tab"]

        # Help buttons
        self.open_help = ["f1"]
        self.close_help = ["escape", "f1"]
        
    @staticmethod
    def render(button_list: list[str]):
        button_list = [button.title() for button in button_list]
        if len(button_list) == 1:
            return button_list[0]
        elif len(button_list) == 2:
            return f"{button_list[0]} and {button_list[1]}"
        else:
            return f"{', '.join(button_list[:-1])} and {button_list[-1]}"
