from sys import exit as sysexit
import pygame as pg
import Textures
import GAME_DATA



def create_translation_dic(textures_dic: dict[int, pg.Surface]) -> dict[int, int]:
    
    """ 
    Créer un dictionnaire de traduction entre les id des textures dans le fichier GAME_DATA
    et un indice montant pour simplfier les passages entre textures
    """

    every_texture_key = enumerate(textures_dic.keys())

    return {translated_idx: key for translated_idx, key in every_texture_key}


def get_keys_pressed() -> str:
    
    """ Capture la pression des touches """

    dic_keys_pressed = {
        pg.K_d: "d",
        pg.K_g: "g",
        pg.K_p: "p",
        pg.K_q: "q",
        pg.K_s: "s",
        pg.K_l: "l"
    }
    keys = pg.key.get_pressed()

    # Renvoie une seule touche à la fois
    for possible_pressed_key in dic_keys_pressed.keys():
        if keys[possible_pressed_key]:
            return dic_keys_pressed[possible_pressed_key]


def print_formatted_level_data(data: list[list[int]]) -> None:
   
    """ Imprime le contenu de la carte en train d'être éditée sous forme de liste """
   
    print(f"\n\nLEVEL DATA ({nb_col}x{nb_row}) : \n\n\n")
    print("[")
    for row_content in data:
        print(row_content, end=",\n")
    print("]")


def reset_level_data(default_texture_nb: int) -> list[list[int]]:

    """ Remet à 0 la liste décrivant le niveau, effaçant donc tout """

    return [[default_texture_nb for _ in range(nb_col)] for _ in range(nb_row)]


def exit_level_editor() -> None:
    
    """ Sort de l'editeur """
    
    pg.quit()
    sysexit()



def draw_map_cache(level: list[list[int]], textures: dict[int, pg.Surface]) -> pg.Surface:
    
    """ Renvoie une surface sur laquelle est dessinée le niveau en fonction de ses dimensions et des textures """
    
    surface = pg.Surface(SCREEN_DIMS)
    surface.fill(PINK)
    for row_idx, row_content in enumerate(level):
        for column_idx, column_content in enumerate(row_content):
            surface.blit(textures[column_content], (column_idx * CELL_DIMS[0], row_idx * CELL_DIMS[1]))
    
    return surface


def draw_inventory_cache(dic_idx_to_textures: dict[int, int], textures: dict[int, pg.Surface]) -> pg.Surface:
    
    """ Renvoie une surface sur laquelle est dessinée "l'inventaire des textures" en fonction des textures """

    surface = pg.Surface(SCREEN_DIMS)
    surface.fill(BLACK)
    slot_idx = 0
    for y in range(nb_row):
        for x in range(nb_col):
            try:
                surface.blit(textures[dic_idx_to_textures[slot_idx]], (x * CELL_DIMS[0], y * CELL_DIMS[1]))
                slot_idx += 1
            except KeyError: # Jpourrais coder ça mais ça passe en vrai :3
                return surface


def draw_instructions(size: str) -> pg.Surface:

    """ 
    Renvoie une surface sur laquelle est dessiné le texte des instructions 
    "size" : small / big
    """
    
    text_height = 8
    ecart_y = 5
    font = pg.font.Font(EDITOR_FONT_PATH, text_height)

    if size == "big":
        surface = pg.Surface((400, 240)) # Pas de transparence = MONTRER
        surface.fill(WHITE)
        instructions_text = [
            "Instructions : ",
            "",
            "SOURIS : ",
            "molette haut : texture suivante",
            "molette bas : texture précédente",
            "click gauche : appliquer la texture",
            "click droit : ouvrir l'inventaire de textures",
            "",
            "CLAVIER :",
            "\"d\" : effacer",
            "\"g\" : montrer la grille",
            "\"p\" : afficher la liste",
            "\"q\" : quitter l'éditeur",
            "\"s\" : cacher les instructions",
            "\"l\" : importer un niveau dans l'éditeur"
        ]

    else:
        surface = pg.Surface((170, 20), pg.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        instructions_text = [
            "\"s\" : instructions"
        ]


    text_idx = 0
    for text_content in instructions_text:
        text_drawn = font.render(text_content, True, BLACK)
        if size == "big":
            surface.blit(text_drawn, (20, 20 + text_idx * (text_height + ecart_y)))
        else:
            surface.blit(text_drawn, (0, text_idx * (text_height + ecart_y)))
        text_idx += 1

    return surface


def draw_grid_cache() -> pg.Surface:
    
    """ Renvoie une surface transparente sur laquelle est dessinée une grille noire """

    font = pg.font.Font(EDITOR_FONT_PATH, 10)
    surface = pg.Surface(SCREEN_DIMS, pg.SRCALPHA)
    ecart_nb_to_grid = 5
    nb = 1

    # Dessiner les lignes verticales
    for x in range(0, SCREEN_DIMS[0], CELL_DIMS[0]):
        column_num = font.render(str(nb), True, BLACK)
        pg.draw.line(surface, (0, 0, 0, 255), (x, 0), (x, SCREEN_DIMS[1]), 2)
        surface.blit(column_num, (x + ecart_nb_to_grid, ecart_nb_to_grid))
        nb += 1
    # dessine une ligne verticale à droite
    pg.draw.line(surface, (0, 0, 0, 255), (SCREEN_DIMS[0]-2, 0), (SCREEN_DIMS[0]-2, SCREEN_DIMS[1]), 2)

    nb = 1

    # Dessiner les lignes horizontales
    for y in range(0, SCREEN_DIMS[1], CELL_DIMS[1]):
        row_num = font.render(str(nb), True, BLACK)
        pg.draw.line(surface, (0, 0, 0, 255), (0, y), (SCREEN_DIMS[0], y), 2)
        surface.blit(row_num, (ecart_nb_to_grid, y + ecart_nb_to_grid))
        nb += 1
    # dessine une ligne horizontale en bas
    pg.draw.line(surface, (0, 0, 0, 255), (0, SCREEN_DIMS[1]-2), (SCREEN_DIMS[0], SCREEN_DIMS[1]-2), 2)

    return surface


def draw_text_texture_id_name(text_id: int, text_name: str) -> pg.Surface:
    
    """ Dessine la texture sous la souris """

    text_height = 9
    surface = pg.Surface((600, 20), pg.SRCALPHA)
    font = pg.font.Font(EDITOR_FONT_PATH, text_height)
    surface.fill((0, 0, 0, 0))
    text = font.render(f"{text_id}: {text_name}", True, BLACK)
    surface.blit(text, (0, 0))

    return surface





raw_screen_dims = (800, 600)
pg.init()
pg.font.init()
pg.display.set_caption("Zelda - EDITOR")

nb_col, nb_row = (16, 11)
CELL_DIMS = (raw_screen_dims[0] // nb_col, raw_screen_dims[1] // nb_row)
SCREEN_DIMS = (CELL_DIMS[0] * nb_col, CELL_DIMS[1] * nb_row) # Recalculation des dimensions de l'écran
SCREEN = pg.display.set_mode(SCREEN_DIMS)
clock = pg.time.Clock()

dic_textures = Textures.load_textures(
    GAME_DATA.dic_textures_name,
    GAME_DATA.liste_textures_size,
    CELL_DIMS
)


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 192, 203)

EDITOR_FONT_PATH = "ressources/fonts/zelda_original.ttf"

# Enlever "dims" du dictionnaire:
dic_textures.pop("dims")

dic_idx_to_text_idx = create_translation_dic(dic_textures)

DEFAULT_GROUND_IDX = 2
level_data = reset_level_data(DEFAULT_GROUND_IDX)

FPS = 30
bool_draw_grid = bool_change_mouse_texture = bool_show_inventory = bool_show_instructions = False
idx = 0
lookup_idx = idx
ticks = 0
ticks_since_last_grid_drawn = ticks_since_last_texture_change = tick_since_last_inventory_update = ticks_since_last_instructions_update = FPS
texture_properties = draw_text_texture_id_name(dic_idx_to_text_idx[0], GAME_DATA.dic_textures_name[dic_idx_to_text_idx[0]])
map_cache = draw_map_cache(level_data, dic_textures)
inventory_cache = draw_inventory_cache(dic_idx_to_text_idx, dic_textures)
grid = draw_grid_cache()


small_instructions_cache = draw_instructions("small")
big_instructions_cache = draw_instructions("big")

small_instructions_width = small_instructions_cache.get_width()
small_instructions_height = small_instructions_cache.get_height()

big_instructions_width  = big_instructions_cache.get_width()
big_instructions_height = big_instructions_cache.get_height()



running = True
while running:

    """ Capture des événements souris """

    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit_level_editor()

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()
            col, row = mouse_pos[0] // CELL_DIMS[0], mouse_pos[1] // CELL_DIMS[1]
            level_data[row][col] = dic_idx_to_text_idx[idx]
            map_cache = draw_map_cache(level_data, dic_textures)

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            inventory_shown = True
            while inventory_shown:
                SCREEN.blit(inventory_cache, (0, 0))
                pg.display.update()
                for inventory_event in pg.event.get():
                    if inventory_event.type == pg.QUIT:
                        exit_level_editor()
                    if inventory_event.type == pg.MOUSEBUTTONDOWN:
                        mouse_pos = pg.mouse.get_pos()
                        col, row = mouse_pos[0] // CELL_DIMS[0], mouse_pos[1] // CELL_DIMS[1]
                        idx = row * nb_col + col
                        if idx > len(dic_idx_to_text_idx):
                            idx = len(dic_idx_to_text_idx) - 1
                        inventory_shown = False

        if event.type == pg.MOUSEWHEEL:
            idx += event.y
            idx = idx % (len(dic_idx_to_text_idx) - 1)


    """ Capture de pression des touches """

    key_pressed = get_keys_pressed()

    if key_pressed == "p":
        print_formatted_level_data(level_data)

    if key_pressed == "d":
        level_data = reset_level_data(DEFAULT_GROUND_IDX)
        map_cache = draw_map_cache(level_data, dic_textures)

    if key_pressed == "g" and ticks_since_last_grid_drawn > 3: # 3 ticks pour ne pas que ça devienne "aléatoire" pour l'user
        bool_draw_grid = not bool_draw_grid
        ticks_since_last_grid_drawn = 0

    if key_pressed == "q":
        exit_level_editor()

    if key_pressed == "s" and ticks_since_last_instructions_update > 5:
        bool_show_instructions = not bool_show_instructions
        ticks_since_last_instructions_update = 0

    if key_pressed == "l":
        new_level = GAME_DATA.global_dic_map_data[int(input("\n\nEntrez l'ID du niveau : \n >> "))]
        level_data = new_level
        map_cache = draw_map_cache(level_data, dic_textures)


    mouse_x, mouse_y = pg.mouse.get_pos()
    cell_x = (mouse_x // CELL_DIMS[0]) * CELL_DIMS[0]
    cell_y = (mouse_y // CELL_DIMS[1]) * CELL_DIMS[1]


    """ Dessin des éléments dans la fenêtre """

    if idx != lookup_idx: # Pour ne pas recalculer le texte sous la souris chaque frame
        texture_properties = draw_text_texture_id_name(dic_idx_to_text_idx[idx],
                                                       GAME_DATA.dic_textures_name[dic_idx_to_text_idx[idx]])
        lookup_idx = idx

    # Le background (liste sur laquelle on travaille)   
    SCREEN.blit(map_cache, (0, 0)) 

    # La texture à la souris
    SCREEN.blit(dic_textures[dic_idx_to_text_idx[idx]], (cell_x, cell_y)) 

    # La grille
    if bool_draw_grid: 
        SCREEN.blit(grid, (0, 0))

    # Les instructions
    if bool_show_instructions:
        SCREEN.blit(big_instructions_cache, (SCREEN_DIMS[0] - big_instructions_width, 
                                  SCREEN_DIMS[1] - big_instructions_height))
    else:
        SCREEN.blit(small_instructions_cache, (SCREEN_DIMS[0] - small_instructions_width, 
                                  SCREEN_DIMS[1] - small_instructions_height))

    # Les propriétés à la souris
    SCREEN.blit(texture_properties, (mouse_x + 20, mouse_y + 20)) 
    pg.display.flip()



    """ Update les ticks et attends pour arriver aux FPS désirés """

    ticks += 1
    ticks_since_last_grid_drawn += 1
    ticks_since_last_texture_change += 1
    tick_since_last_inventory_update += 1
    ticks_since_last_instructions_update += 1

    clock.tick(FPS)


"""

KEYMAPPING  :

- Mousewheelup : idx += 1
- Mousewheeldown : idx -= 1
- left click : ajouter texture à level_data
- right click : afficher inventaire
- g : afficher la grille
- p : imprimer carte
- d : delete la carte actuelle
- q : quit

"""
