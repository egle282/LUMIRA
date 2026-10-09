from typing import Dict, Any, List
from datetime import datetime

class DestinyMatrixNode:
    def __init__(self, position: str, value: int, description: str):
        self.position = position # e.g., 'center', 'top', 'bottom', 'karmic_tail'
        self.value = value
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "value": self.value,
            "description": self.description
        }

class DestinyMatrixEngine:
    """
    Deterministic calculation engine for the Destiny Matrix (Матрица Судьбы).
    This is based on the 22 Major Arcana archetypes calculated from the birth date.
    """
    
    def __init__(self):
        pass
        
    def _reduce_to_arcana(self, num: int) -> int:
        """
        Reduces a number to a valid Major Arcana number (1-22).
        If the number > 22, its digits are summed.
        """
        while num > 22:
            num = sum(int(digit) for digit in str(num))
        # In Destiny Matrix, 0 is often considered 22
        if num == 0:
            return 22
        return num

    def calculate_matrix(self, birth_date: datetime) -> Dict[str, Any]:
        """
        Calculates the core nodes of the Destiny Matrix.
        """
        day = birth_date.day
        month = birth_date.month
        year = birth_date.year
        
        # 1. Personal Portrait (Day)
        portrait = self._reduce_to_arcana(day)
        
        # 2. Connection to Higher Self / Guardian Angel (Month)
        higher_self = self._reduce_to_arcana(month)
        
        # 3. Material Karma / Past Life Finance (Year)
        year_sum = sum(int(d) for d in str(year))
        material_karma = self._reduce_to_arcana(year_sum)
        
        # 4. Karmic Tail / Past Life Unresolved Karma (Bottom node)
        # Usually calculated as Portrait + Higher Self + Material Karma
        bottom_sum = portrait + higher_self + material_karma
        karmic_tail = self._reduce_to_arcana(bottom_sum)
        
        # 5. Center (Comfort Zone)
        center_sum = portrait + higher_self + material_karma + karmic_tail
        center = self._reduce_to_arcana(center_sum)
        
        nodes = [
            DestinyMatrixNode("portrait", portrait, "Your outward personality and how others see you."),
            DestinyMatrixNode("higher_self", higher_self, "Your spiritual connection and intuition."),
            DestinyMatrixNode("material_karma", material_karma, "Your material blockages and financial lessons from past lives."),
            DestinyMatrixNode("karmic_tail", karmic_tail, "Deep karmic lessons and negative patterns to resolve."),
            DestinyMatrixNode("center", center, "Your comfort zone, soul essence, and point of harmony.")
        ]
        
        return {
            "birth_date": birth_date.isoformat(),
            "nodes": [node.to_dict() for node in nodes]
        }
