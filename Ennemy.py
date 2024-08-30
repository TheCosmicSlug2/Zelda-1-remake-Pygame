from math import log
from settings import *
from random import randint, choice
import pygame as pg  # Ajoutez cette ligne si ce n'est pas déjà fait
from entity import Entity
from utils import message
from particle import Projectile



class DefEnnemy(Entity):
    def __init__(self, 
                 player, 
                 level_master,
                 spawning_id: int,
                 cell_coords: tuple,
                 dims=DEF_ENNEMY_DIMS,
                 health: int=DEF_ENNEMY_HEALTH, 
                 speed: float=DEF_ENNEMY_SPEED, 
                 attack_power: int=DEF_ENNEMY_ATTACK_POWER):
        super().__init__()

        self.class_name = "Ennemy"

        self.player = player
        self.level_master = level_master
        self.spawning_ID = spawning_id

        self.dims = dims
        

        # Au final on fait spawn en en haut à gauche de la cellule, pour qu'il soit centré
        self.posx = cell_coords[0] * self.level_master.cell_dims[0]                
        self.posy = cell_coords[1] * self.level_master.cell_dims[1]

        self.width, self.height = dims[0], dims[1]
        self.speed = speed

        self.dx, self.dy = 0, 0
        self.health = health
        self.attack_power = attack_power
        self.check_movement_collision = True
        self.hitsound = sfx_ennemy_hit
        self.deathsound = sfx_ennemy_death
        self.play_hitsound, self.play_deathsound = True, True

        self.state = 0 # Immobile (1 : mobile aléatoire, 2: mobile cherche player)
        self.target_cell = None
        self.idle_tick = 0
        self.been_spawned_tick = 0
        self.target_idle_tick = randint(0, FPS * 2)

        self.is_on_target_cell = True

        self.dir = choice(self.physics.possible_dirs)

        self.tick_until_self_shows = randint(10, TICK_UNTIL_ENNEMY_SHOWS)

        self.throw_projectiles = False
        self.projectile_thrown = False
        self.projectile = None


    def trouver_dst_orth_to_player(self) -> tuple:

        """ Trouve l'écart x et y séparant du joueur """

        player_middle_coords = (self.player.width // 2, self.player.height // 2)

        dst_x = self.player.posx + player_middle_coords[0] - self.posx
        dst_y = self.player.posy + player_middle_coords[1] - self.posy
        return dst_x, dst_y
    

    def trouver_dst_orth_to_pos(self) -> tuple:

        dst_x = self.target_cell_pos[0] - self.posx
        dst_y = self.target_cell_pos[1] - self.posy
        return dst_x, dst_y
    

    

    def collide_player(self):

        """ Checke une collision basique avec le rectangle du joueur """
        
        return self.physics.check_collision(self.player.posx, self.player.posy, self.player.width, self.player.height, self.posx, self.posy, self.width, self.height)

    
    def check_is_on_target_cell(self):
        self.physics.check_collision(self.target_cell_pos[0], self.target_cell_pos[1], self.player.cellsize_x, self.player.cellsize_y, self.posx, self.posy, self.width, self.height)


    def update_projectile(self):
        if not self.throw_projectiles:
            return
        
        self.projectile.move()
        

    def do_something(self, update=False):

        # OK CA MARCHE, faut juste cleanup (variables et conditions plus clean) + rélger BAT AI + grid snapping de l'ennemi

        # Si l'ennemi est immobile, on checke si il est immobile depuis déjà assez longtemps*

        if self.been_spawned_tick < self.tick_until_self_shows:
            self.been_spawned_tick += 1
            return
        

        if self.state == 0:
            if self.type == "leever":
                self.target_idle_tick = 0 # Pas de répit pour la leever                

            if self.idle_tick == 0 and self.throw_projectiles and not self.projectile_thrown:
                self.projectile.init_to_ennemy(self.posx, self.posy, self.dir)
                self.projectile_thrown = True

            if self.idle_tick >= self.target_idle_tick:
                self.idle_tick = 0
                self.state = randint(1, 2)            
            else:
                self.idle_tick += 1

        if self.state != 0 and self.check_movement_collision and self.is_on_target_cell:

            self.posx, self.posy = self.physics.get_snapped_pos(
                                    (self.posx, self.posy),
                                    (self.width, self.height),
                                    self.level_master.cell_dims
            )


            self.dir = choice(self.physics.possible_dirs)

            
            self.dx = self.physics.dic_dir_to_movement[self.dir][0]
            self.dy = self.physics.dic_dir_to_movement[self.dir][1]


            self.dst_x = randint(1, 4) * self.level_master.cell_dims[0]
            self.dst_y = randint(1, 4) * self.level_master.cell_dims[1]

            self.travelled_dst_x = 0
            self.travelled_dst_y = 0

            self.is_on_target_cell = False
                


        if self.state != 0 and self.check_movement_collision and not self.is_on_target_cell: 

            possible_next_pos_x = self.posx + self.dx * self.speed
            possible_next_pos_y = self.posy + self.dy * self.speed

            if self.physics.check_4_side_collision((possible_next_pos_x, possible_next_pos_y), self.dims, self.level_master.current_map_data, (self.level_master.nb_column, self.level_master.nb_row), self.level_master.cell_dims):
                self.is_on_target_cell = True
                self.state = 0
                self.target_idle_tick = randint(0, FPS * 2)
            else:
                # Avancer

                self.posx = possible_next_pos_x
                self.posy = possible_next_pos_y

                self.travelled_dst_x += self.dx * self.speed
                self.travelled_dst_y += self.dy * self.speed        

                if abs(self.travelled_dst_x) >= self.dst_x or abs(self.travelled_dst_y) >= self.dst_y:
                    self.is_on_target_cell = True
                    self.state = 0
                    self.target_idle_tick = randint(0, FPS * 2)

        if self.state != 0 and not self.check_movement_collision and not self.is_on_target_cell:

            dst_x, dst_y = self.trouver_dst_orth_to_pos()
            angle_to_target = self.physics.trouver_angle_to_target(dst_x, dst_y)

            if update:
                        
                # Met à jour dx et dy en fonction de l'angle vers le joueur
                self.dx, self.dy = self.physics.calculer_trigos_to_target(angle_to_target)

            self.posx += self.dx
            self.posy += self.dy


        if self.collide_player():
            self.player.react_to_hit(direction=self.dir)


        # Projectile :
        if self.projectile_thrown:
            self.update_projectile()
            if self.projectile.check_touch_border():
                self.projectile_thrown = False
            if self.projectile.check_for_player_collision():
                self.projectile_thrown = False
                if self.projectile.dir == self.get_translated_player_dir():
                    pg.mixer.Sound.play(sfx_shield_defuse)
                    return
                self.player.react_to_hit(self.projectile.dir)

    
    def get_translated_player_dir(self):
        dic = {
            "haut": "bas",
            "bas": "haut",
            "droite": "gauche",
            "gauche": "droite"
        }

        return dic[self.player.dir]
            

    def go_to_player(self, update=False) -> None:

        """ Effectue les calculs de pathfinding et avance vers le joueur """

        vitesse_attaque = 1

        if update:
            dst_x, dst_y = self.trouver_dst_orth_to_player()
            dst_to_player = self.trouver_hypothenuse(dst_x, dst_y)
            angle_to_player = self.trouver_angle_to_target(dst_x, dst_y)
            self.dx, self.dy = self.calculer_trigos_to_target(angle_to_player)
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

        self.health -= amount
        if self.health <= 0:
            self.health = 0


        hit_impact = self.physics.dic_dir_to_movement[knockback_dir]
        possible_next_pos_x = self.posx + (hit_impact[0] * PLAYER_KNOCKBACK_FORCE)
        possible_next_pos_y = self.posy + (hit_impact[1] * PLAYER_KNOCKBACK_FORCE)

        if self.physics.check_4_side_collision((possible_next_pos_x, possible_next_pos_y), self.dims, self.level_master.current_map_data, (self.level_master.nb_column, self.level_master.nb_row), self.level_master.cell_dims):
            loop_count = 0 # Pas la meilleure solution 
            while self.physics.check_4_side_collision((possible_next_pos_x, possible_next_pos_y), self.dims, self.level_master.current_map_data, (self.level_master.nb_column, self.level_master.nb_row), self.level_master.cell_dims):
                possible_next_pos_x -= hit_impact[0] * (CELLSIZE_X // 2)
                possible_next_pos_y -= hit_impact[1] * (CELLSIZE_Y // 2)

                loop_count += 1
                if loop_count > 10:
                    message(origin_class=self, var_tuple=(self, "collision_error"))
                    break


                # Au lieu d'enlever 1 unité par 1 unité, on enlève une demi-cellule

        self.posx = possible_next_pos_x
        self.posy = possible_next_pos_y


    def get_raw_rect_sprite(self) -> pg.Rect:
        
        """ Retourne la hitbox de l'ennemi """

        return pg.Rect(self.posx, self.posy, self.width, self.height)


    def check_drop_something(self):
        return randint(0, 1), (self.posx, self.posy)
    

    def get_has_been_spawned_costume(self):
        if self.been_spawned_tick < self.tick_until_self_shows:
            if self.been_spawned_tick < self.tick_until_self_shows // 3:
                return 601
            if self.been_spawned_tick < 2 * (self.tick_until_self_shows // 3):
                return 602
            else:
                return 603
        return None



class Bat(DefEnnemy):
    def __init__(self, level_master, player, spawning_id, cell_coords):
        super().__init__(player, level_master, spawning_id, cell_coords, health=30, speed=BAT_SPEED)

        self.dims = BAT_DIMS
        self.type = "bat"

        self.check_movement_collision = False

    @staticmethod
    def get_sprite_id(game_tick):
        return 301 if game_tick < 15 else 302



class Octorok(DefEnnemy):
    
    """ Pieuvre """

    def __init__(self, player, level_master, spawning_id, cell_coords, color, speed=None):
        super().__init__(player, level_master, spawning_id, cell_coords, health=60)

        
        self.dims = OCTOROK_DIMS
        self.type = "octorok"

        if speed == "slow":
            self.speed = OCTOROK_SLOW_SPEED
        if speed == "fast":
            self.speed = OCTOROK_FAST_SPEED


        self.posx -= self.width // 2
        self.posy -= self.width // 2
        self.color = color
        if self.color == "rouge":
            self.health = OCTOROK_RED_HEALTH
        else:
            self.health = OCTOROK_BLUE_HEALTH

        self.throw_projectiles = True
        self.projectile = Projectile(self.player)


    def go_to_player(self, update=False) -> None:
        
        raise("Fais gaffe t'as des checks de collision qui existent pas là")

        dst_x, dst_y = self.trouver_dst_orth_to_player()
        angle_to_player = self.physics.trouver_angle_to_target(dst_x, dst_y)

        if update:
            # Met à jour dx et dy en fonction de l'angle vers le joueur
            self.dx, self.dy = self.physics.calculer_trigos_to_target(angle_to_player)

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

        spawn_costume = self.get_has_been_spawned_costume()
        if spawn_costume:
            return spawn_costume

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

    def __init__(self, level_master, player, spawning_id, cell_coords, color, speed):
        super().__init__(player, level_master, spawning_id, cell_coords, health=60)
        self.dims = LEEVER_DIMS

        self.type = "leever"

        self.color = color

        if speed == "slow":
            self.speed = OCTOROK_SLOW_SPEED
        if speed == "fast":
            self.speed = OCTOROK_FAST_SPEED
        
        if self.color == "rouge":
            self.health = LEEVER_RED_HEALTH
        if self.color == "bleu":
            self.health == LEEVER_BLUE_HEALTH

        self.posx -= self.width // 2
        self.posy -= self.width // 2
        


    def go_to_player(self, update=False) -> None:
        
        """ Ici : mouvement aléatoire, pas vers le joueur """

        if update:
            if randint(0, 1) == 0:
                new_cell_x = randint(0, self.level_master.nb_column-1)
                new_cell_y = randint(0, self.level_master.nb_row-1)

                if self.player.map_data[new_cell_y][new_cell_x] < 10: # pas la meilleure manière de faire : bcp de calculs
                    self.posx, self.posy = new_cell_x * self.level_master.cell_dims[0] + self.level_master.cell_dims[0] // 2 - self.width // 2, \
                                           new_cell_y * self.player.cell_dims[1] + self.level_master.cell_dims[1] // 2 - self.height // 2
        if self.collide_player():
            self.player.react_to_hit()


    def get_sprite_id(self, game_tick):

        spawn_costume = self.get_has_been_spawned_costume()
        if spawn_costume:
            return spawn_costume

        # 5 frames pour le leever
        leever_costume_tick = game_tick // 2
        if leever_costume_tick < 7:
            self.play_hitsound = True
            dec = 0
        else: 
            dec = 1

        if self.color == "rouge":
            return 334 + dec ### AATTENTION Y'A TOUT LE DEBUT D4ANIMATION QUI EST PAS PRIS EN COMPTE
        return 339 + dec
