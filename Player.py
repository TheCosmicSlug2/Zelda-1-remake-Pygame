from Settings import *
from random import randint
from time import sleep
from GAME_DATA import global_dic_map_data

class Player:
    def __init__(self, game, dic_textures) -> None:
        self.width, self.height = PLAYER_DIMS
        self.game = game
        self.posx = game.screen_game_dims[0] // 2 + self.width // 2
        
        self.hitbox_height = self.height / 4
        self.hitbox_height_dec = self.height - self.hitbox_height
        
        self.relative_posy = game.screen_game_dims[1] // 2 + self.height // 2
        self.map_data = game.map_data
        self.nb_row, self.nb_column = game.nb_row, game.nb_column
        self.cellsize_x, self.cellsize_y = game.cellsize_x, game.cellsize_y

        self.tick_counter = 0

        self.dic_textures = dic_textures
        
       
        self.dic_loot = {}
        
        self.speed = PLAYER_SPEED
        self.ecart_y, self.ecart_x = 0, 0
        
        self.dir = "haut"
        self.attack_power = PLAYER_ATTACK_POWER
        self.play_attack_sfx = True
        self.snapped_to_grid = False

        self.max_health = PLAYER_LIFE
        self.health = PLAYER_LIFE
        self.coins = 0
        self.keys = 0
        self.bombs = 0
        self.invicible = False
        self.tick_invicibility = 0


    """ 
    I/ UIs / update
    II/ Collisions
    III/ Attaques
    IV/ Loots
    V/ Sprite
    """


    """ I/ UIs """

    def update_to_map(self) -> None:
        """ Update les données de la liste """
        self.map_data = self.game.map_data
        self.nb_row, self.nb_column = self.game.nb_row, self.game.nb_column
        self.cellsize_x, self.cellsize_y = self.game.cellsize_x, self.game.cellsize_y
    

    def draw_ui_cache(self, level_id: int) -> None:

        self.ui_cache = pg.Surface(self.game.screen_ui_dims)
        self.ui_cache.fill(BLACK)

        self.update_ui_cache_minimap(level_id)
        self.update_ui_cache_coins()
        self.update_ui_cache_keys()
        self.update_ui_cache_bombs()
        self.update_ui_cache_life()


    def update_ui_cache_minimap(self, level_id: int) -> None:
        ratio = 10
        nb_level_column = 16
        nb_level_row = len(global_dic_map_data) // 16

        largeur_minimap = nb_level_column * ratio
        hauteur_minimap = nb_level_row * ratio

        minimap = pg.Surface((largeur_minimap, hauteur_minimap))
        minimap.fill(COLOR_MINIMAP)

        ##### ATTENTION LEVEL_ID COMMENCE A 1 : OBLIGE DE SOUSTRAIRE 1 POUR COLLER A LA MAP

        current_level_square = pg.Surface((largeur_minimap // nb_level_column, hauteur_minimap // nb_level_row))
        current_level_square.fill(COLOR_MINIMAP_CURRENT_lEVEL)
        current_level_square_pos = ((level_id - 1) % nb_level_column * ratio, (level_id - 1) // nb_level_column * ratio)

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



    """ II/ Collisions, mvts """

    def check_level_trigger(self) -> bool:
        
        """ Capture la position (x, y) et retourne un changement d'écran si elle est < 0 ou > dimensions de l'écran """
        
        level_triggered = False
        if self.posx < 0:
            self.posx = self.game.screen_game_dims[0] - ecart_new_level
            level_triggered = True

        if self.posx + self.width >= self.game.screen_game_dims[0]:
            self.posx = ecart_new_level - self.width
            level_triggered = True

        if self.relative_posy < 0:
            self.relative_posy = self.game.screen_game_dims[1] - ecart_new_level
            level_triggered = True

        if self.relative_posy + self.height > self.game.screen_game_dims[1]:
            self.relative_posy = ecart_new_level - self.height
            level_triggered = True

        return level_triggered


    def check_player_wall_collisions(self, dir: str) -> bool:

        """ Capture les collisions du joueur (conditions pour collisions haut, gauche, droite => identiques) """


        cell_x_bas_gauche = int(self.posx // self.cellsize_x)
        cell_y_bas_gauche = int((self.relative_posy + self.height) // self.cellsize_y)

        cell_x_bas_droit = int((self.posx + self.width) // self.cellsize_x)
        cell_y_bas_droit = int((self.relative_posy + self.height) // self.cellsize_y)

        cell_y_bas_plus_hitbox = int((self.relative_posy + self.hitbox_height_dec) // self.cellsize_y)
        
        try:
            if dir == "bas":
                if self.map_data[cell_y_bas_gauche][cell_x_bas_gauche] > 50: # Problème de collisions fatal ici 
                    return True
                if self.map_data[cell_y_bas_droit][cell_x_bas_droit] > 50:
                    return True
            else:
                if self.map_data[cell_y_bas_plus_hitbox][cell_x_bas_gauche] > 50:
                    return True
                if self.map_data[cell_y_bas_plus_hitbox][cell_x_bas_droit] > 50:
                    return True
        except Exception as e:
            print("Exception non fatale rencontrée : ", e)
            return True

        return False


    def move(self):

        """ Tente de déplacer le joueur selon le mouvement demandé, c'est à dire les touches pressées """

        movement = self.dir

        if movement == "haut":
            self.relative_posy -= self.speed
            if self.check_level_trigger():
                return movement
            while self.check_player_wall_collisions(movement):
                self.relative_posy += 1
            self.ecart_y = 0 # Dummy variable pour résoudre mini problèmes de positions

        if movement == "bas":
            self.relative_posy += self.speed
            if self.check_level_trigger():
                return movement
            while self.check_player_wall_collisions(movement):
                self.relative_posy -= 1
            self.ecart_y = 1

        if movement == "gauche":
            self.posx -= self.speed
            if self.check_level_trigger():
                return movement
            while self.check_player_wall_collisions(movement):
                self.posx += 1
            self.ecart_x = 0

        if movement == "droite":
            self.posx += self.speed
            if self.check_level_trigger():
                return movement
            while self.check_player_wall_collisions(movement):
                self.posx -= 1
            self.ecart_x = 1

        return None


    def snap_to_grid(self):

        """ Snap le joueur à la grille (unité : 1/2 cellule)"""

        half_cell_x = round(self.posx / (self.cellsize_x // 2)) # On snap à la cellule entière au final
        half_cell_y = round(self.relative_posy / (self.cellsize_y // 2))
        self.posx = half_cell_x *(self.cellsize_x // 2) + self.cellsize_x // 4 - self.width // 4
        self.relative_posy = half_cell_y * (self.cellsize_y // 2) + self.cellsize_y // 4 - self.height // 4
        self.snapped_to_grid = True



    """ III/ Attaques / défenses """

    def attack(self, liste_ennemies: list) -> None:
        if self.play_attack_sfx:
            pg.mixer.Sound.play(sfx_sword_slash)
        self.play_attack_sfx = False
        attack_rect = self.get_raw_rect_attack_sprite()
        for enemy in liste_ennemies:
            if attack_rect.colliderect(enemy.get_raw_rect_sprite()):
                enemy.take_damage(self.attack_power, self.dir)
    

    def react_to_hit(self, direction: str=None): # La direction de l'ennemi attention

        """ Réagit à une attaque ennemie """

        if self.invicible:
            return
        
        if self.check_player_wall_collisions(direction):
            return 

        self.health -= 0.5

        self.update_ui_cache_life()
        pg.mixer.Sound.play(sfx_link_hit)

        dic_hits_dir = {"bas": (0, 1), "gauche": (-1, 0), "haut": (0, -1), "droite": (1, 0)}

        if not direction:
            # Si y'a pas de direction ATTENTION CAHNGER CA
            self.posx += randint(-10, 10)
            self.relative_posy += randint(-10, 10)
            self.invicible = True
            return
        

        hit_impact = dic_hits_dir[direction]
        self.posx += hit_impact[0] * DEF_ENNEMY_KNOCKBACK
        self.relative_posy += hit_impact[1] * DEF_ENNEMY_KNOCKBACK

        if self.check_player_wall_collisions(direction):
            while self.check_player_wall_collisions(direction):
                self.posx -= hit_impact[0]
                self.relative_posy -= hit_impact[1]
        
        self.invicible = True
        


    """ IV/ Loot """

    def grab_loot(self, liste_loot: list):

        """ Itère sur tous les loots présents à l'écran et checke une collision """

        for loot in liste_loot:
            # 2 méthodes : soit colliderect soit à l'ancienne
            if not self.game.check_collision(self.posx, self.relative_posy, self.width, self.height, loot.posx, loot.posy, loot.dims[0], loot.dims[1]):
                continue
            
            if loot.loot_type == "coin_yellow":
                pg.mixer.Sound.play(sfx_get_yellow_rupy)
                self.coins += 1
                self.update_ui_cache_coins()

            elif loot.loot_type == "coin_blue":
                pg.mixer.Sound.play(sfx_get_blue_rupy)
                self.coins += 5
                self.update_ui_cache_coins()

            elif loot.loot_type == "heart_small":
                pg.mixer.Sound.play(sfx_get_heart_or_key)
                self.health = min(self.health + 1, self.max_health)
                self.update_ui_cache_life()

            elif loot.loot_type == "heart_big":
                self.max_health += 1
                self.health = self.max_health
                self.update_ui_cache_life()
            else:
                print(f"Loot \"{loot.loot_type}\" non trouvé")

            liste_loot.remove(loot)



    """ V/ Sprites """

    def get_raw_rect_passive_sprite(self) -> pg.Rect:

        """ Retourne le hitbox passive """

        return pg.Rect(self.posx + self.ecart_x, self.game.screen_ui_dims[1] + self.relative_posy + self.ecart_y, self.width, self.height)

    def get_raw_rect_attack_sprite(self) -> pg.Rect:

        """ Retourne la hitbox d'attaque """

        dic = {"bas": (0, 1), "gauche": (-1, 0), "haut": (0, -1), "droite": (1, 0)}
        arme_dir = self.dir
        arme_x, arme_y = dic[arme_dir]
        arme_width, arme_height = abs(arme_x * WEAPON_1), abs(arme_y * WEAPON_1)
        """
        (0,             height,         0,              arme_height) # bas
        (0,             -arme_height,   0,              arme_height) # haut
        (-arme_width,   0,              arme_width,     0) # gauche
        (width,         0,              arme_width,     0) # droite
        """
        if arme_dir == "bas":

            return pg.Rect(self.posx , self.relative_posy + self.height,
                           self.width, arme_height)
        if arme_dir == "haut":
            return pg.Rect(self.posx, self.relative_posy - arme_height,
                           self.width, arme_height)
        if arme_dir == "gauche":
            return pg.Rect(self.posx - arme_width, self.relative_posy,
                           arme_width, self.height)
        if arme_dir == "droite":
            return pg.Rect(self.posx + self.width, self.relative_posy,
                           arme_width, self.height)
    