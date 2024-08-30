from settings import *
from random import randint, choice
from game_data import dic_world
from entity import Entity
from utils import message


"""
La classe du Joueur
"""

class Player(Entity):
    def __init__(self, level_master, dic_textures) -> None:
        super().__init__()
        self.class_name = "Player"
        
        self.level_master = level_master

        self.width, self.height = PLAYER_DIMS
        self.hitbox_height = PLAYER_HITBOX_HEIGHT
        self.hitbox_height_dec = PLAYER_HITBOX_HEIGHT_DEC

        self.posx = SCREEN_GAME_DIMS[0] // 2 + self.width // 2
        self.posy = SCREEN_GAME_DIMS[1] // 2 + self.height // 2
        self.ecart_y, self.ecart_x = 0, 0

        self.dir = "haut"

        self.tick_counter = 0

        self.dic_textures = dic_textures
        
       
        self.dic_loot = {}
        
        self.speed = PLAYER_SPEED

        self.is_moving = True
        self.is_attacking = False

        self.triggered_level_transition = False
        self.current_level_transition = None

        self.attack_power = PLAYER_ATTACK_POWER
        self.tick_attack = 0
        self.play_attack_sfx = True
        

        self.max_health = PLAYER_MAX_HEALTH
        self.health = PLAYER_HEALTH

        self.coins = 0
        self.keys = 0
        self.bombs = 0

        self.invicible = False
        self.tick_invicibility = 0

        self.debug_idx = 0


    """ 
    I/ UI / update
    II/ Collisions
    III/ Attaques
    IV/ Loots
    V/ Sprite
    """


    """ I/ UI : la barre noire dessinée en haut de l'écran """    

    def draw_ui_cache(self) -> None:

        self.ui_cache = pg.Surface(SCREEN_UI_DIMS)
        self.ui_cache.fill(BLACK)

        self.update_ui_cache_minimap()
        self.update_ui_cache_coins()
        self.update_ui_cache_keys()
        self.update_ui_cache_bombs()
        self.update_ui_cache_life()


    def update_ui_cache_minimap(self) -> None:
        ratio = 10
        nb_level_column = 16
        nb_level_row = len(dic_world) // 16

        largeur_minimap = nb_level_column * ratio
        hauteur_minimap = nb_level_row * ratio

        minimap = pg.Surface((largeur_minimap, hauteur_minimap))
        minimap.fill(COLOR_MINIMAP)

        ##### ATTENTION LEVEL_ID COMMENCE A 1 : OBLIGE DE SOUSTRAIRE 1 POUR COLLER A LA MAP

        current_level_square = pg.Surface((largeur_minimap // nb_level_column, hauteur_minimap // nb_level_row))
        current_level_square.fill(COLOR_MINIMAP_CURRENT_lEVEL)
        current_level_square_pos = ((self.level_master.current_level_ID - 1) % nb_level_column * ratio, (self.level_master.current_level_ID - 1) // nb_level_column * ratio)

        minimap.blit(current_level_square, current_level_square_pos)


        self.ui_cache.blit(minimap, (40, 60))


    def update_ui_cache_coins(self) -> None:
        
        coin_cache = pg.Surface((120, 20))
        coin_cache.fill(BLACK)
        coin_cache.blit(self.dic_textures[1001], (0, 0))
        text_coins = zelda_font.render("x" + str(self.coins), True, WHITE)
        coin_cache.blit(text_coins, (30, 0))
        self.ui_cache.blit(coin_cache, (220, 60))
    

    def update_ui_cache_keys(self) -> None:

        key_cache = pg.Surface((120, 20))
        key_cache.fill(BLACK)
        key_cache.blit(self.dic_textures[1002], (0, 0))
        text_keys = zelda_font.render("x" + str(self.keys), True, WHITE)
        key_cache.blit(text_keys, (30, 0))
        self.ui_cache.blit(key_cache, (220, 100))


    def update_ui_cache_bombs(self) -> None:

        bomb_cache = pg.Surface((120, 20))
        bomb_cache.fill(BLACK)
        bomb_cache.blit(self.dic_textures[1003], (0, 0))
        text_bombs = zelda_font.render("x" + str(self.bombs), True, WHITE)
        bomb_cache.blit(text_bombs, (30, 0))
        self.ui_cache.blit(bomb_cache, (220, 120))


    def update_ui_cache_life(self) -> None:

        health_cache = pg.Surface((200, 80))
        health_cache.fill(BLACK)
        text_health_title = zelda_font.render("-LIFE-", True, COLOR_LIFE)
        health_cache.blit(text_health_title, (0, 0))

        ecart = 1
        
        nb_hearts_per_line = 10

        if self.max_health > nb_hearts_per_line:
            current_nb_hearts_on_top_line = self.max_health - nb_hearts_per_line
        else:
            current_nb_hearts_on_top_line = 0

        for row in range(2):

            if row == 1 and current_nb_hearts_on_top_line == 0:
                continue

            for column in range(current_nb_hearts_on_top_line):

                # La première ligne est donc vide si pas assez de maw health

                # On dessine la ligne du haut

                if self.health - (10 + column) <= 0:
                    heart_texture_id = 401
                elif self.health - (10 + column) <= 0.5:
                    heart_texture_id = 402
                else:
                    heart_texture_id = 403
                
                health_cache.blit(self.dic_textures[heart_texture_id], (column * (HEART_DIMS[0] + ecart), 50))
            
            current_nb_hearts_on_bottom_line = (self.max_health - current_nb_hearts_on_top_line)
            
            for column in range(current_nb_hearts_on_bottom_line):

                # La première ligne est donc vide si pas assez de maw health

                # On dessine la ligne du haut
                if self.health - (column) <= 0:
                    heart_texture_id = 401
                elif self.health - (column) <= 0.5:
                    heart_texture_id = 402
                else:
                    heart_texture_id = 403
                
                
                health_cache.blit(self.dic_textures[heart_texture_id], (column * (HEART_DIMS[0] + ecart), 60))

        self.ui_cache.blit(health_cache, (500, 60))
    
    
    def snap_to_grid(self):
        self.posx, self.posy = self.physics.get_snapped_pos(
            (self.posx, self.posy),
            (self.width, self.height),
            self.level_master.cell_dims
        )



    """ II/ Collisions, mvts """

    def check_level_trigger(self) -> bool:
        
        """ Capture la position (x, y) et retourne un changement d'écran si elle est < 0 ou > dimensions de l'écran """
        
        if self.posx < 0:
            self.posx = SCREEN_GAME_DIMS[0] - ecart_new_level
            return True

        if self.posx + self.width >= SCREEN_GAME_DIMS[0]:
            self.posx = ecart_new_level - self.width
            return True

        if self.posy < 0:
            self.posy = SCREEN_GAME_DIMS[1] - ecart_new_level
            return True

        if self.posy + self.height > SCREEN_GAME_DIMS[1]:
            self.posy = ecart_new_level - self.height
            return True

        return False
    

    def adjust_pos_to_scrollage(self, scrollage_dir):

        """ Ajuste la position du joueur en fonction de la transition d'écran """

        dic_scrollage_to_pos = {

            "bas": (
                (0, -SCREEN_GAME_DIMS[1]),
                (0, 1)
            ),

            "gauche": (
                (SCREEN_GAME_DIMS[0], 0),
                (-1, 0)
                ),

            "haut": (
                (0, SCREEN_GAME_DIMS[1]),
                (0, -1)
                ),

            "droite": (
                (-SCREEN_GAME_DIMS[0], 0),
                (1, 0)
                )
        }

        if scrollage_dir.startswith("get"):
            return

        new_pos_factor, ecart = dic_scrollage_to_pos[scrollage_dir]

        self.posx += new_pos_factor[0] + CELLSIZE_X * ecart[0]
        self.posy += new_pos_factor[1] + CELLSIZE_Y * ecart[1]
    

    def adjust_pos_to_get_into_secret(self):
        self.posx = SCREEN_GAME_DIMS[0] // 2
        self.posy = SCREEN_GAME_DIMS[1] - self.height
    

    def adjust_pos_to_get_out_of_secret(self):
        self.posx = self.level_master.current_secret_position[0] * self.level_master.cell_dims[0]
        self.posy = self.level_master.current_secret_position[1] * self.level_master.cell_dims[1] + self.height + 5


    def move(self):

        self.debug_idx = 0

        """ Tente de déplacer le joueur selon le mouvement demandé, c'est à dire les touches pressées """

        mvt_dir = self.dir

        dic_dir_to_mvt = {
            "bas": (0, 1),
            "gauche": (-1, 0),
            "haut": (0, -1),
            "droite": (1, 0)
        }

        delta_speed = dic_dir_to_mvt[mvt_dir]

        self.posx += delta_speed[0] * self.speed
        self.posy += delta_speed[1] * self.speed

        # TODO : Si on est dans une caverne, changer ça

        scroll_direction = self.physics.get_is_touching_screen_border(
            SCREEN_GAME_DIMS, 
            (self.posx, self.posy),
            (self.width, self.height)
        )
        
        if scroll_direction:
            self.triggered_level_transition = True
            self.current_level_transition = scroll_direction

        
            if self.level_master.current_world_type == "cavern":
                self.current_level_transition = "get_out_secret"

            if self.level_master.current_world_type == "dungeon" and self.level_master.current_level_ID == 216 and self.current_level_transition == "bas":
                self.current_level_transition = "get_out_secret"

        while self.physics.check_4_side_collision(
            (self.posx, self.posy + self.hitbox_height_dec), 
            (self.width, self.hitbox_height), 
            self.level_master.current_map_data,
            self.level_master.current_map_data_dims,
            self.level_master.cell_dims,
            ):
            self.posx -= delta_speed[0]
            self.posy -= delta_speed[1]

            self.debug_idx += 1

            # Si il y a trop de collisions bizarres, on met le joueur dans un endroit safe le + vite possible
            if self.debug_idx > 50:
                self.debug_collision_error()
        

    def debug_collision_error(self):

        """ Met le joueur au premier endroit libre que la fonction trouve """

        for row_idx, row in enumerate(self.level_master.current_map_data):
            for column_idx, column in enumerate(row):
                if column < 50:
                    self.posx = column_idx * self.level_master.cell_dims[0]
                    self.posy = row_idx * self.level_master.cell_dims[1]
                    message(origin_class=self, message="The collisions were a little \"fancy\" here... Can you pwease stay outta that spot ? :3")
                    return


    def collide_ennemy(self, enemy):
        attack_rect = self.get_raw_rect_attack_sprite()
        return attack_rect.colliderect(enemy.get_raw_rect_sprite())



    """ III/ Attaques / défenses """

    def attack(self, liste_ennemies: list) -> None:
        if self.play_attack_sfx:
            pg.mixer.Sound.play(sfx_sword_slash)
        self.play_attack_sfx = False
        for enemy in liste_ennemies:
            if self.collide_ennemy(enemy):
                enemy.take_damage(self.attack_power, self.dir)
    

    def react_to_hit(self, direction: str=None): # La direction de l'ennemi attention

        """ Réagit à une attaque ennemie """

        if self.invicible:
            return

        self.health -= 0.5
        self.health = max(self.health, 0)

        self.update_ui_cache_life()
        pg.mixer.Sound.play(sfx_link_hit)

        if not direction:
            # Si y'a pas de direction ATTENTION CAHNGER CA
            self.posx += randint(-20, 20)
            self.posy += randint(-20, 20)
            self.invicible = True
            return
        

        hit_impact = self.physics.dic_dir_to_movement[direction]
        self.posx += hit_impact[0] * DEF_ENNEMY_KNOCKBACK
        self.posy += hit_impact[1] * DEF_ENNEMY_KNOCKBACK

        while self.physics.check_4_side_collision(
            (self.posx, self.posy + self.hitbox_height_dec), 
            (self.width, self.hitbox_height), 
            self.level_master.current_map_data,
            self.level_master.current_map_data_dims,
            self.level_master.cell_dims
            ):
            self.posx -= hit_impact[0] * (CELLSIZE_X // 2)
            self.posy -= hit_impact[1] * (CELLSIZE_Y // 2)
        
        self.invicible = True


    def react_to_projectile_hit(self, dir):        
        self.react_to_hit(dir)
        


    """ IV/ Loot """

    def grab_loot(self, liste_loot: list):

        """ Itère sur tous les loots présents à l'écran et checke une collision """

        for loot in liste_loot:
            # 2 méthodes : soit colliderect soit à l'ancienne
            if not self.physics.check_collision(self.posx, self.posy, self.width, self.height, loot.posx, loot.posy, loot.dims[0], loot.dims[1]):
                continue

            
            if loot.type == "coin_yellow":
                pg.mixer.Sound.play(sfx_get_yellow_rupy)
                self.coins += 1
                self.update_ui_cache_coins()

            elif loot.type == "coin_blue":
                pg.mixer.Sound.play(sfx_get_blue_rupy)
                self.coins += 5
                self.update_ui_cache_coins()

            elif loot.type == "heart_small":
                pg.mixer.Sound.play(sfx_get_heart_or_key)
                self.health = min(self.health + 1, self.max_health)
                self.update_ui_cache_life()

            elif loot.type == "heart_big":
                self.max_health += 1
                self.health = self.max_health
                self.update_ui_cache_life()
            else:
                message(origin_class=self, message="Loot", var_tuple=(loot.type, "non trouvé"))

            liste_loot.remove(loot)



    """ V/ Sprites """

    def get_raw_rect_passive_sprite(self) -> pg.Rect:

        """ Retourne le hitbox passive """

        return pg.Rect(self.posx + self.ecart_x, SCREEN_UI_DIMS[1] + self.posy + self.ecart_y, self.width, self.height)


    def get_raw_rect_attack_sprite(self) -> pg.Rect:

        """ Retourne la hitbox d'attaque """

        arme_dir = self.dir
        arme_x, arme_y = self.physics.dic_dir_to_movement[arme_dir]
        arme_width, arme_height = abs(arme_x * WEAPON_DIMS[0]), abs(arme_y * WEAPON_DIMS[1])
        """
        (0,             height,         0,              arme_height) # bas
        (0,             -arme_height,   0,              arme_height) # haut
        (-arme_width,   0,              arme_width,     0) # gauche
        (width,         0,              arme_width,     0) # droite
        """
        if arme_dir == "bas":

            return pg.Rect(self.posx , self.posy + self.height,
                           self.width, arme_height)
        if arme_dir == "haut":
            return pg.Rect(self.posx, self.posy - arme_height,
                           self.width, arme_height)
        if arme_dir == "gauche":
            return pg.Rect(self.posx - arme_width, self.posy,
                           arme_width, self.height)
        if arme_dir == "droite":
            return pg.Rect(self.posx + self.width, self.posy,
                           arme_width, self.height)
        

    def get_moving_sprite(self, moving_tic: int) -> pg.surface:

        """ Pour n'importe quel tick, renvoie l'exacte animation de mouvement de link """

        ecart_beetween_moving_pos = 4 # Pour chaque frame de marche, 3 frame de dégâts

        dic_player_costumes = {
            "bas": 201,
            "gauche": 211,
            "haut": 221,
            "droite": 231
        }

        base_direction_costume = dic_player_costumes[self.dir] + moving_tic * ecart_beetween_moving_pos
        return self.dic_textures[base_direction_costume + (self.tick_invicibility % ecart_beetween_moving_pos)]


    def get_attack_sprite(self, attack_tic: int) -> pg.surface:

        """ Pour n'importe quel tick, renvoie l'exacte animation d'attaque de link """

        dic_player_costumes = {
            "bas": 241,
            "gauche": 251,
            "haut": 261,
            "droite": 271
        }

        base_direction_costume = dic_player_costumes[self.dir]
        return self.dic_textures[base_direction_costume + self.tick_invicibility % 4] # + attack_tic


    def get_weapon_sprite(self):
        
        # Pour l'instant que l'épée bleue
        dic_weapon_costumes = { 
            "bas": 505,
            "gauche": 506,
            "haut": 507,
            "droite": 508
        }

        base_direction_costume = dic_weapon_costumes[self.dir]
        return self.dic_textures[base_direction_costume] # + attack_tic


    def get_weapon_position(self, attack_tick):

        decalage = attack_tick * 4

        ecart_start_anim = 3 # Dummy variable

        if self.dir == "bas":
            ecart_x = 8 # L'arme n'est pas alignée avec la main
            weapon_pos = (self.posx + ecart_x, self.posy + self.height - ecart_start_anim - decalage)
        if self.dir == "gauche":
            ecart_y = 3
            weapon_pos = (self.posx - self.width + ecart_start_anim + decalage, self.posy + ecart_y)
        if self.dir == "haut":
            weapon_pos = (self.posx, self.posy - self.height + ecart_start_anim + decalage)
        if self.dir == "droite":
            ecart_y = 3
            weapon_pos = (self.posx + self.width - ecart_start_anim - decalage, self.posy + ecart_y)
        
        return weapon_pos
    
