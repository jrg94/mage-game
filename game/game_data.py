import game_spells

class Character():
    def __init__(self):
        self.palette = [
            game_spells.Projectile(game_spells.Element.FIRE), 
            game_spells.Projectile(game_spells.Element.WATER)
        ]
        self.current_spell = self.palette[0]
        
    def generate_modifiers(self):
        return {
            'speed_in_pixels': self.current_spell.speed_level * 10,
            'radius_in_pixels': self.current_spell.radius_level * 5,
            'life_in_frames': self.current_spell.distance_level * 15,
            'color_in_rgb': self.current_spell.element.color
        }