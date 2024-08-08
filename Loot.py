from random import randint
from Settings import *

class Loot:
    def __init__(self, posx: int, posy: int, player):
        self.dic_loot_rng_to_type = {
            0: ("heart_small", HEART_DIMS), 
            1: ("heart_big", HEART_BIG_DIMS), 
            2: ("coin_yellow", COIN_DIMS), 
            3: ("coin_blue", COIN_DIMS)
            }
        self.posx, self.posy = posx, posy
        loot_rng = randint(0, 10)

        # 0 - 2 : heart
        # 3 - 5 : coin_yellow
        # 6 - 8 : coin_blue
        # 9 - 10 : big_heart

        if loot_rng < 3:
            loot_idx = 0
        elif loot_rng < 6:
            loot_idx = 2
        elif loot_rng < 9:
            loot_idx = 3
        else:
            loot_idx = 1

        self.loot_type, self.dims = self.dic_loot_rng_to_type[loot_idx] # Indice négatif si aucun loot
        self.sprite_id = self.get_sprite_id()
        self.player = player


    def get_sprite_id(self):
        
        """
        Retourne l'ID de la texture en fonction du type de loot
        """

        dic_loot_types_to_costume = {
            "heart_small": 403, 
            "heart_big": 405,
            "coin_yellow": 411, 
            "coin_blue": 412
        }

        return dic_loot_types_to_costume[self.loot_type]

