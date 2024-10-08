from main_menu import *
import pygame as pg
from math import floor
from utils import message


"""
Si tu veux changer un truc sur le jeu, c'est ici
Fait pas de la merde sinon tout va exploser
Ducoup partout où y'a un "#", tu peux changer, mais ça va ptet exploser quand même
"""


filename = "settings.py"

""" Settings général du jeu / joueur / ennemis """

pg.init()
pg.font.init()

zelda_font = pg.font.Font("ressources/fonts/zelda_original.ttf", 20)

# Game
# Pour le jeu zelda 1, l'ui fait 270 px et le "jeu" fait 740

# Largeur recommandée : 1080 px pour 1000

RAW_SCREEN_HEIGHT = 600 #
RAW_SCREEN_WIDTH = 800 #

rapport_ui_fen = 265 / 1000
rapport_game_fen = 735 / 1000

original_setting = False
if original_setting:
    # Pas obligé : juste pour coller à l'original
    rapport_fen_width_height = 1080 / 1000
    RAW_SCREEN_WIDTH = RAW_SCREEN_HEIGHT * rapport_fen_width_height # PAS OBLIGE HEIN JUSTE POUR ORIGINAL


UI_HEIGHT = int(RAW_SCREEN_HEIGHT * rapport_ui_fen)
GAME_HEIGHT = int(RAW_SCREEN_HEIGHT * rapport_game_fen)

nb_column, nb_rows = 16, 11

FULLSCREEN = False
RAW_SCREEN_DIMS = (RAW_SCREEN_WIDTH, UI_HEIGHT + GAME_HEIGHT)


recalculated_width = RAW_SCREEN_DIMS[0] // nb_column * nb_column
screen_game_height = ((RAW_SCREEN_DIMS[1] - UI_HEIGHT) // nb_rows) * nb_rows 


SCREEN_DIMS = (recalculated_width, RAW_SCREEN_DIMS[1])
SCREEN_GAME_DIMS = (recalculated_width, screen_game_height)
SCREEN_UI_DIMS = (recalculated_width, SCREEN_DIMS[1] - SCREEN_GAME_DIMS[1])

CELLSIZE_X, CELLSIZE_Y = SCREEN_GAME_DIMS[0] // nb_column, SCREEN_GAME_DIMS[1] // nb_rows

# Recalculer les dimensions de l'écran
SCREEN_GAME_WIDTH, SCREEN_GAME_HEIGHT = CELLSIZE_X * nb_column, CELLSIZE_Y * nb_rows 

message(filename=filename, var_tuple=(
    "Anciennes dimension", RAW_SCREEN_DIMS, 
    "recalculées à", SCREEN_DIMS,
    "UI", SCREEN_UI_DIMS,
    "GAME", SCREEN_GAME_DIMS)
    )


if False:
    FULLSCREEN = True
    SCREEN_WIDTH, SCREEN_HEIGHT = pg.display.Info().current_w, pg.display.Info().current_h


HALF_SCREEN_WIDTH, HALF_SCREEN_HEIGHT = SCREEN_GAME_WIDTH // 2, SCREEN_GAME_HEIGHT // 2
RES = (SCREEN_DIMS[0], SCREEN_DIMS[1])



# Couleurs
# Tout ça tu peux changer 

WHITE = (255, 255, 255) 
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
COLOR_MINIMAP = (102, 102, 102)
COLOR_MINIMAP_CURRENT_lEVEL = (211, 210, 255)
COLOR_LIFE = (181, 49, 32)

dic_colors = {0: WHITE, 1: BLACK}


# Player
PLAYER_DIMS = (floor(SCREEN_GAME_DIMS[0] / 16) - 2, floor(SCREEN_GAME_DIMS[1] / 11) - 2) # - 2 : valeur arbitraire pour pas de fausses collisions
HALF_PLAYER_DIMS = (PLAYER_DIMS[0] // 2, PLAYER_DIMS[1] // 2)
PLAYER_HITBOX_HEIGHT = round(PLAYER_DIMS[1] / 4)
PLAYER_HITBOX_HEIGHT_DEC = PLAYER_DIMS[1] - PLAYER_HITBOX_HEIGHT

# Tout ça tu peux changer
NB_TICKS_TO_UPDATE_PLAYER = 4
NB_TICK_PLAYER_INVICIBILITY = 60

WEAPON_DIMS = PLAYER_DIMS
PLAYER_KNOCKBACK_FORCE = 30

PLAYER_SPEED = int(CELLSIZE_X * 0.15)
PLAYER_MAX_HEALTH = 3
PLAYER_HEALTH = 3
PLAYER_ATTACK_POWER = 10

ecart_new_level = int((CELLSIZE_X + CELLSIZE_Y) // 2) * 2 # moyenne des dimensions de la cellule 
# Inutile de mettre un mini écart en plus au cas où étant donné qu'il clipe automatiquement à la cellule la + proche
# Au final si on va mettre 2x l'écart pour être sûr

# ça tu peux changer
DEF_ENNEMY_DIMS = (20, 20)
DEF_ENNEMY_HEALTH = 10
DEF_ENNEMY_SPEED = 50
DEF_ENNEMY_COLOR = (255, 0, 0)
DEF_ENNEMY_HEALTH = 50
DEF_ENNEMY_ATTACK_POWER = 2

DEF_ENNEMY_KNOCKBACK = 100

TICK_UNTIL_ENNEMY_SHOWS = 20

BAT_DIMS = (16*2, 11*2)
BAT_SPEED = 5
BAT_HEALTH = PLAYER_ATTACK_POWER
OCTOROK_DIMS = (CELLSIZE_X - 10, CELLSIZE_Y - 10)
OCTOROK_SLOW_SPEED = 3
OCTOROK_FAST_SPEED = 5
OCTOROK_RED_HEALTH = 20
OCTOROK_BLUE_HEALTH = 30
LEEVER_DIMS = (CELLSIZE_X - 10, CELLSIZE_Y - 10)
LEEVER_SLOW_SPEED = 3
LEEVER_FAST_SPEED = 5
LEEVER_RED_HEALTH = 20
LEEVER_BLUE_HEALTH = 30


COIN_DIMS = (20, 30)
HEART_DIMS = (20, 20)
HEART_BIG_DIMS = (40, 40)

FPS = 30

# SFX
pg.mixer.init()
# CA SI TU CHANGES CA EXPLOSE
#song_main_menu = pg.mixer.Sound("ressources/sfx/main_menu.mp3")
song_overworld = pg.mixer.Sound("ressources/sfx/overworld.mp3")
sfx_ennemy_hit = pg.mixer.Sound("ressources/sfx/ennemy_hit.mp3")
sfx_ennemy_death = pg.mixer.Sound("ressources/sfx/ennemy_dead.mp3")
sfx_link_hit = pg.mixer.Sound("ressources/sfx/link_hit.mp3")
sfx_link_dead = pg.mixer.Sound("ressources/sfx/link_dead.mp3")
sfx_sword_slash = pg.mixer.Sound("ressources/sfx/sword_slash.mp3")
sfx_get_yellow_rupy = pg.mixer.Sound("ressources/sfx/get_yellow_rupy.mp3")
sfx_get_blue_rupy = pg.mixer.Sound("ressources/sfx/get_blue_rupy.mp3")
sfx_get_heart_or_key = pg.mixer.Sound("ressources/sfx/get_heart_or_key.mp3")
sfx_stairs = pg.mixer.Sound("ressources/sfx/stairs.mp3")
sfx_shield_defuse = pg.mixer.Sound("ressources/sfx/shield_defuse.mp3")



# Et ça tu peux changer autant que tu veux
STARTING_LEVEL = 120
MIN_ENNEMIES_PER_LEVEL = 1 
MAX_ENNEMIES_PER_LEVEL = 5 # Essaye de mettre 10 000, si t'as un bon pc tu vas kiffer 


VISU_TIME = 0.1 # Variable débug

