import game_spells

class Character():
    def __init__(self):
        self.palette = [
            game_spells.Projectile(game_spells.Element.FIRE), 
            game_spells.Projectile(game_spells.Element.WATER),
            game_spells.Projectile(game_spells.Element.EARTH),
            game_spells.Projectile(game_spells.Element.AIR),
        ]
        self.current_spell_index = 0
        
    def generate_modifiers(self):
        current_spell = self.palette[self.current_spell_index]
        return {
            'speed_in_pixels': current_spell.speed_level * 10,
            'radius_in_pixels': current_spell.radius_level * 5,
            'life_in_frames': current_spell.distance_level * 15,
            'color_in_rgb': current_spell.element.color
        }