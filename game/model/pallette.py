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
    
    def update_cooldowns(self, dt: float) -> bool:
        for spell in self.spells.keys():
            self.spells[spell] = self.spells[spell] - dt
            if self.spells[spell] <= 0:
                self.spells[spell] = 0
                
    def can_cast_active_spell(self) -> bool:
        return self.spells[self.get_active_spell()] == 0
    
    def reset_active_spell_cooldown(self):
        active_spell = self.get_active_spell()
        self.spells[active_spell] = active_spell.cooldown() * 1000
        