from game_data import *
from settings import *
from utils import message


"""
C'est, genre, la classe la plus importante de tout ce projet :
Elle sait tout ce qui est fondamental : les dimensions du niveau actuel, la taille des cellules...
En gros, c'est un traducteur entre les données "brutes" (game_data.py) et les autres fichiers qui gèrent les éléments du jeu (ennemies.py, player.py, main.py...)

"""

class LevelMaster: 
    
    """ le maitre du changement de level :) """

    def __init__(self):
        self.class_name = "LevelMaster"

        self.current_level_ID = STARTING_LEVEL
        self.current_world_type = "overworld"

        self.update_to_new_level()

    

    def update_to_new_level(self):

        self.current_map_data = dic_world[self.current_level_ID]
        self.nb_column = len(self.current_map_data[0])
        self.nb_row = len(self.current_map_data)
        self.current_map_data_dims = (self.nb_column, self.nb_row)

        self.cell_dims = (CELLSIZE_X, CELLSIZE_Y)

        self.current_ennemy_positions = global_dic_ennemy_nb_positions[self.current_level_ID]

        self.current_secret = global_dic_secret_location[self.current_level_ID]

        if self.current_secret:
            self.current_secret_exist = True
            self.current_secret_position = self.current_secret
            self.current_secret_type = None
        else:
            self.current_secret_exist = False
            self.current_secret_position = None
            

        message(origin_class=self, var_tuple=("Current level ID", self.current_level_ID, "current secret location", self.current_secret_position))


    def change_level(self, scroll_direction: str) -> int:

        """ prend un id de map, et direction de sortie du joueur => renvoie nouvel id de map, map qui doit suivre """

        # bas : 0
        # gauche : 1
        # haut : 2
        # droite : 3
        
        new_level_id = None

        dic_scroll_direction = {
            "bas": 0,
            "gauche": 1,
            "haut": 2,
            "droite": 3,
            "get_in_secret": 4,
            "get_out_secret": 0
        }

        nb_dir = dic_scroll_direction[scroll_direction]

        new_level_id = global_dic_scrollage[self.current_level_ID][nb_dir]

        self.current_level_ID = new_level_id

        self.update_to_new_level()
