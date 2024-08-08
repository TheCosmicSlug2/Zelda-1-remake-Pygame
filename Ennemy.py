from math import cos, sin, sqrt, atan2, log
from Settings import *
from random import randint
import pygame as pg  # Ajoutez cette ligne si ce n'est pas déjà fait


class DefEnnemy:
    def __init__(self, player, spawning_id: int,
                 cell_coords: tuple,
                 dims=DEF_ENNEMY_DIMS,
                 health: int=DEF_ENNEMY_HEALTH, speed: float=DEF_ENNEMY_SPEED, attack_power: int=DEF_ENNEMY_ATTACK_POWER):

        self.player = player
        self.spawning_ID = spawning_id

        self.dims = dims

        # Au final on fait spawn en en haut à gauche de la cellule, pour qu'il soirt centré
        self.posx, self.posy = cell_coords[0] * self.player.cellsize_x, \
                               cell_coords[1] * self.player.cellsize_y

        self.width, self.height = dims[0], dims[1]
        self.speed = speed

        self.dx, self.dy = 0, 0
        self.health = health
        self.attack_power = attack_power
        self.hitsound = sfx_ennemy_hit
        self.deathsound = sfx_ennemy_death
        self.play_hitsound, self.play_deathsound = True, True


    def trouver_dst_orth_to_player(self) -> tuple:

        """ Trouve l'écart x et y séparant du joueur """

        player_middle_coords = (self.player.width // 2, self.player.height // 2)

        dst_x = self.player.posx + player_middle_coords[0] - self.posx
        dst_y = self.player.relative_posy + player_middle_coords[1] - self.posy
        return dst_x, dst_y


    @staticmethod
    def trouver_hypothenuse(dst_x: int, dst_y: int) -> float:

        """ Trouve la longueur de l'hypothénuse à partir des 2 autres côtés """

        hyp = sqrt(dst_x**2 + dst_y**2)
        return hyp


    @staticmethod
    def trouver_angle_to_player(dst_x: int, dst_y: int) -> float:

        """ Trouve l'angle au joueur à partir de l'hypothénuse et de l'adjacent """

        angle_to_player = atan2(dst_y, dst_x)
        return angle_to_player


    @staticmethod
    def calculer_trigos_to_player(angle: float) -> tuple[int, int]:

        """ Calcule les distances dx et dy en fonction de l'angle actuel """

        dx = cos(angle)
        dy = sin(angle)
        return dx, dy


    def check_wall_collisions(self) -> bool:

        """ Capture les collisions avec le niveau (conditions pour collisions haut, gauche, droite => identiques) """

        cell_x_bas_droit = int((self.posx + self.width) // self.player.cellsize_x)
        cell_y_bas_droit = int((self.posy + self.height) // self.player.cellsize_y)

        cell_x_bas_gauche = int(self.posx // self.player.cellsize_x)
        cell_y_bas_gauche = int((self.posy + self.height) // self.player.cellsize_y)

        
        try:
            if self.player.map_data[cell_y_bas_gauche][cell_x_bas_gauche] > 50: # Problème de collisions fatal ici 
                return True
            if self.player.map_data[cell_y_bas_droit][cell_x_bas_droit] > 50:
                return True
        except Exception as e:
            print("Exception non fatale rencontrée : ", e)
            return True

        return False


        return False


    def collide_player(self):

        """ Checke une collision basique avec le rectangle du joueur """

        return self.player.game.check_collision(self.player.posx, self.player.relative_posy, self.player.width, self.player.height, self.posx, self.posy, self.width, self.height)


    def go_to_player(self, update=False) -> None:

        """ Effectue les calculs de pathfinding et avance vers le joueur """

        vitesse_attaque = 1

        if update:
            dst_x, dst_y = self.trouver_dst_orth_to_player()
            dst_to_player = self.trouver_hypothenuse(dst_x, dst_y)
            angle_to_player = self.trouver_angle_to_player(dst_x, dst_y)
            self.dx, self.dy = self.calculer_trigos_to_player(angle_to_player)
            self.dx += randint(0, 1)
            self.dy += randint(0, 1)

            vitesse_attaque = max(log(self.speed / dst_to_player), 2)


        self.posx += vitesse_attaque * self.dx
        self.posy += vitesse_attaque * self.dy


    def take_damage(self, amount: int, knockback_dir: str) -> None:
        
        """ Enlève à l'ennemi la quantité de vie adéquate """

        if self.play_hitsound:
            pg.mixer.Sound.play(self.hitsound)
            self.play_hitsound = False
        dic_knock_back_dir = {"bas": (0, 1), "gauche": (-1, 0), "haut": (0, -1), "droite": (1, 0)}
        knockback_force = 10
        self.health -= amount
        if self.health <= 0:
            self.health = 0

        dx, dy = dic_knock_back_dir[knockback_dir]

        self.posx += dx * knockback_force
        self.posy += dy * knockback_force


    def get_raw_rect_sprite(self) -> pg.Rect:
        
        """ Retourne la hitbox de l'ennemi """

        return pg.Rect(self.posx, self.posy, self.width, self.height)


    def check_drop_something(self):
        return randint(0, 1), (self.posx, self.posy)



class Bat(DefEnnemy):
    def __init__(self, player, spawning_id, cell_coords):
        super().__init__(player, spawning_id, cell_coords, health=30, speed=2.0)

        self.dims = BAT_DIMS

    @staticmethod
    def get_sprite_id(game_tick):
        return 301 if game_tick < 15 else 302



class Octorok(DefEnnemy):
    
    """ Pieuvre """

    def __init__(self, player, spawning_id, cell_coords, color):
        super().__init__(player, spawning_id, cell_coords, health=60, speed=1.0)
        self.dims = OCTOROK_DIMS

        self.posx -= self.width // 2
        self.posy -= self.width // 2
        self.color = color
        if self.color == "rouge":
            self.health = 30
        else:
            self.health = 60
        self.dir = "haut"


    def go_to_player(self, update=False) -> None:
        dst_x, dst_y = self.trouver_dst_orth_to_player()
        angle_to_player = self.trouver_angle_to_player(dst_x, dst_y)

        if update:
            # Met à jour dx et dy en fonction de l'angle vers le joueur
            self.dx, self.dy = self.calculer_trigos_to_player(angle_to_player)

        vitesse_attaque = self.speed if update else 1

        if abs(self.dx) > abs(self.dy):
            if self.dx < 0:
                self.dir = "gauche"
            else:
                self.dir = "droite"

            if not self.check_wall_collisions():
                self.posx += vitesse_attaque * self.dx
        else:
            if self.dy < 0:
                self.dir = "haut"
            else:
                self.dir = "bas"

            if not self.check_wall_collisions():
                self.posy += vitesse_attaque * self.dy

        if self.collide_player():
            
            self.player.react_to_hit(direction=self.dir)


    def get_sprite_id(self, game_tick):
        dec = 0
        if self.dir == "bas":
            dec = 0
        if self.dir == "gauche":
            dec = 2
        if self.dir == "haut":
            dec = 4
        if self.dir == "droite":
            dec = 6

        if self.color == "rouge":
            if game_tick < 15:
                self.play_hitsound = True
                return 311 + dec
            else:
                return 312 + dec
        else:
            if game_tick < 15:
                self.play_hitsound = True
                return 321 + dec
            else:
                return 322 + dec



class Leever(DefEnnemy):
    
    """ Pyramide qui sort du sol """

    def __init__(self, player, spawning_id, cell_coords, color):
        super().__init__(player, spawning_id, cell_coords, health=60, speed=1.0)
        self.dims = LEEVER_DIMS
        self.posx -= self.width // 2
        self.posy -= self.width // 2
        #### ATTENTON SI Y'A PAS DE SELF DIRECTION : PLAYER SE RETROUVE COINCE DANS LES MURS
        self.color = color


    def go_to_player(self, update=False) -> None:
        
        """ Ici : mouvement aléatoire, pas vers le joueur """

        if update:
            if randint(0, 1) == 0:
                new_cell_x = randint(0, self.player.nb_column-1)
                new_cell_y = randint(0, self.player.nb_row-1)

                if self.player.map_data[new_cell_y][new_cell_x] < 10: # pas la meilleure manière de faire : bcp de calculs
                    self.posx, self.posy = new_cell_x * self.player.cellsize_x + self.player.cellsize_x // 2 - self.width // 2, \
                                           new_cell_y * self.player.cellsize_y + self.player.cellsize_y // 2 - self.height // 2
        if self.collide_player():
            self.player.react_to_hit()


    def get_sprite_id(self, game_tick):
        # 5 frames pour le leever
        fifth_of_tick = FPS / 5
        if game_tick < fifth_of_tick:
            self.play_hitsound = True
            dec = 0
        elif game_tick < 2 * fifth_of_tick:
            dec = 1
        elif game_tick < 3 * fifth_of_tick:
            dec = 2
        elif game_tick < 4 * fifth_of_tick:
            dec = 3
        else:
            dec = 4

        if self.color == "rouge":
            return 331 + dec
        return 336 + dec

