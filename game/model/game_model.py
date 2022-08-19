from model import spells

class GameState():
    def __init__(self):
        self.palette = [
            spells.Projectile(spells.Element.FIRE), 
            spells.Projectile(spells.Element.WATER),
            spells.Projectile(spells.Element.EARTH),
            spells.Projectile(spells.Element.AIR),
        ]
        self.current_spell_index = 0
