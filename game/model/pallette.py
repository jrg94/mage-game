from model import spells as spell_module
from dataclasses import dataclass, field

@dataclass
class Palette:
    spells: dict[spell_module.Projectile: float] = field(default_factory=lambda: {
        spell_module.Projectile(spell_module.Element.FIRE): 0, 
        spell_module.Projectile(spell_module.Element.WATER): 0,
        spell_module.Projectile(spell_module.Element.EARTH): 0,
        spell_module.Projectile(spell_module.Element.AIR): 0,
    })
    current_spell_index: int = 0
    
    def get_active_spell(self) -> spell_module.Projectile:
        return list(self.spells.keys())[self.current_spell_index]
        