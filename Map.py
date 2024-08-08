from Settings import *
from random import randint
from GAME_DATA import global_dic_map_data


class Map:
    def __init__(self, level_id: int):
        self.map_data = global_dic_map_data[level_id]
        self.nb_row, self.nb_column = len(self.map_data), len(self.map_data[0])
        self.cellsize_x, self.cellsize_y = round(SCREEN_GAME_WIDTH / self.nb_column), round(SCREEN_GAME_HEIGHT / self.nb_row)
        

    def draw_map_cache(self, dic_textures: dict) -> pg.surface:

        """ Dessine une surface de background avec les textures et les actuelles données de la map """

        image_size_x, image_size_y = dic_textures["dims"]
        surface = pg.Surface((SCREEN_GAME_WIDTH, SCREEN_GAME_HEIGHT))
        surface.fill(BLACK)

        for row_idx, row_content in enumerate(self.map_data):
            for column_idx, column_content in enumerate(row_content):
                surface.blit(dic_textures[column_content], (column_idx * image_size_x, row_idx * image_size_y))
                
        return surface


    def change_level(self, new_level_id: int, game_textures: dict) -> None:

        """ Change les informations que le level possède sur l'état du jeu """

        self.map_data = global_dic_map_data[new_level_id]
        self.nb_row, self.nb_column = len(self.map_data), len(self.map_data[0])
        self.cellsize_x, self.cellsize_y = round(SCREEN_GAME_WIDTH / self.nb_column), round(SCREEN_GAME_HEIGHT / self.nb_row)



class MiniMap:
    def __init__(self, sizex: int, sizey: int, map_data: list):
        self.sizex, self.sizey = sizex, sizey
        self.data_world = map_data