from GAME_DATA import *
from Settings import STARTING_LEVEL


class LevelMaster: 
    """ le maitre du changement de level :) """

    def __init__(self):
        self.current_level_ID = STARTING_LEVEL

    @staticmethod
    def change_level(ancient_level_id: int, scroll_direction: str) -> int:

        """ prend un id de map, et direction de sortie du joueur => renvoie id, map qui doit suivre """

        # bas : 0
        # gauche : 1
        # haut : 2
        # droite : 3
        
        new_level_id = None

        if scroll_direction == "bas":
            new_level_id = global_dic_scrollage[ancient_level_id][0]

        if scroll_direction == "gauche":
            new_level_id = global_dic_scrollage[ancient_level_id][1]

        if scroll_direction == "haut":
            new_level_id = global_dic_scrollage[ancient_level_id][2]

        if scroll_direction == "droite":
            new_level_id = global_dic_scrollage[ancient_level_id][3]

        return new_level_id