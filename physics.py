from math import atan2, sqrt, cos, sin
from utils import message


"""
Classe pour handle la physique du jeu
"""

class Physics:
    def __init__(self) -> None:
        self.dic_dir_to_movement = {
            "bas": (0, 1),
            "gauche": (-1, 0),
            "haut": (0, -1),
            "droite": (1, 0)
        }

        self.possible_dirs = ["bas", "gauche", "haut", "droite"]


    @staticmethod
    def check_collision(x1, y1, w1, h1, x2, y2, w2, h2):

        """ Fonction globale pour checker les collisions """

        return x1 + w1 > x2 and x2 + w2 > x1 and y1 + h1 > y2 and y2 + h2 > y1
    
    
    @staticmethod
    def check_4_side_collision(top_left_pos, object_dims, liste, liste_dims, cell_dims, debug=False):
        
        """ Putain c'est chiant les collisions """

        # La "vrai" position du joueur est invisible

        top_left_pos = (round(top_left_pos[0]), round(top_left_pos[1]))

        if debug:
            message(filename="Physics", var_tuple=("top_left_pos", top_left_pos))

        # Obtenir la position absolue des 4 côtés
        top_right_pos = (top_left_pos[0] + object_dims[0], top_left_pos[1])
        bottom_left_pos = (top_left_pos[0], top_left_pos[1] + object_dims[1])
        bottom_right_pos = (top_right_pos[0], bottom_left_pos[1])

        cell_top_left_pos = (top_left_pos[0] // cell_dims[0], top_left_pos[1] // cell_dims[1])
        cell_top_right_pos = (top_right_pos[0] // cell_dims[0], top_left_pos[1] // cell_dims[1])
        cell_bottom_left_pos = (bottom_left_pos[0] // cell_dims[0], bottom_left_pos[1] // cell_dims[1])
        cell_bottom_right_pos = (bottom_right_pos[0] // cell_dims[0], bottom_right_pos[1] // cell_dims[1])

        if cell_top_left_pos[0] < 0 or cell_top_left_pos[1] < 0:
            return True
        if cell_bottom_right_pos[0] > liste_dims[0] - 1 or cell_bottom_right_pos[1] > liste_dims[1] - 1:
            return True

        cell_top_left = liste[cell_top_left_pos[1]][cell_top_left_pos[0]]
        cell_top_right = liste[cell_top_right_pos[1]][cell_top_right_pos[0]]
        cell_bottom_left = liste[cell_bottom_left_pos[1]][cell_bottom_left_pos[0]]
        cell_bottom_right = liste[cell_bottom_right_pos[1]][cell_bottom_right_pos[0]]

        return cell_top_left > 50 or cell_top_right > 50 or cell_bottom_left > 50 or cell_bottom_right > 50


    @staticmethod
    def trouver_hypothenuse(dst_x: int, dst_y: int) -> float:

        """ Trouve la longueur de l'hypothénuse à partir des 2 autres côtés """

        hyp = sqrt(dst_x**2 + dst_y**2)
        return hyp


    @staticmethod
    def trouver_angle_to_target(dst_x: int, dst_y: int) -> float:

        """ Trouve l'angle au joueur à partir de l'hypothénuse et de l'adjacent """

        angle_to_player = atan2(dst_y, dst_x)
        return angle_to_player


    @staticmethod
    def calculer_trigos_to_target(angle: float) -> tuple[int, int]:

        """ Calcule les distances dx et dy en fonction de l'angle actuel """

        dx = cos(angle)
        dy = sin(angle)
        return dx, dy
    

    @staticmethod
    def get_snapped_pos(entity_pos, entity_dims, cell_dims) -> tuple[int, int]:

        """ Snap l'entiy à la grille (unité : 1/2 cellule)"""

        half_cell_x = round(entity_pos[0] / (cell_dims[0] // 2)) # On snap à la cellule entière au final
        half_cell_y = round(entity_pos[1] / (cell_dims[1] // 2))
        posx = half_cell_x * (cell_dims[0] // 2) + cell_dims[0] // 4 - entity_dims[0] // 4
        posy = half_cell_y * (cell_dims[1] // 2) + cell_dims[1] // 4 - entity_dims[1] // 4

        return posx, posy
    
    @staticmethod
    def get_is_touching_screen_border(screen_dims, entity_pos, entity_dims):

        if entity_pos[0] < 0:
            return "gauche"
        
        if entity_pos[0] + entity_dims[0] > screen_dims[0]:
            return "droite"
        
        if entity_pos[1] < 0:
            return "haut"
        
        if entity_pos[1] + entity_dims[1] > screen_dims[1]:
            return "bas"
        
        return None
    
    @staticmethod
    def is_touching_cell(entity_pos, entity_dims, target_cell_pos, target_cell_dims, global_cellsize):
        
        """ Pour l'instant, rudimentaire mais améliorer """
        """ Ne checke que le coin haut gauche """

        cell_x = entity_pos[0] // global_cellsize[0]
        cell_y = entity_pos[1] // global_cellsize[1]

        return cell_x == target_cell_pos[0] and cell_y == target_cell_pos[1]
    
    @staticmethod
    def is_touching_secret(entity_pos, entity_dims, entity_dir, secret_cell_grid_pos, global_cellsize):
        if entity_dir == "bas":
            if entity_pos[1] <= secret_cell_grid_pos[1] * global_cellsize[1] and entity_pos[0] == secret_cell_grid_pos[0] * global_cellsize[0]:
                return True
        if entity_dir == "gauche":
            if entity_pos[0] + entity_dims[0] <= secret_cell_grid_pos[0] * global_cellsize[0] + global_cellsize[0] and entity_pos[1] == secret_cell_grid_pos[1] * global_cellsize[1]:
                return True
        if entity_dir == "haut":
            if entity_pos[1] + entity_dims[1] <= secret_cell_grid_pos[1] * global_cellsize[1] + global_cellsize[1] and entity_pos[0] == secret_cell_grid_pos[0] * global_cellsize[0]:
                return True
        if entity_dir == "droite":
            if entity_pos[0] >= secret_cell_grid_pos[0] * global_cellsize[0] and entity_pos[1] == secret_cell_grid_pos[1] * global_cellsize[1]:
                return True

        return False
