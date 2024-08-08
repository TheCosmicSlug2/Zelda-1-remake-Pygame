import time
import Textures
from Player import Player
from Map import *
from Change_level import *
from Ennemy import DefEnnemy, Bat, Octorok, Leever
from Loot import Loot
from sys import exit as sysexit


class Game:
    def __init__(self, res: tuple, fullscreen: bool) -> None:
        self.screen_dims = res
        self.screen_game_dims = SCREEN_GAME_DIMS
        self.screen_ui_dims = SCREEN_UI_DIMS
        self.SCREEN = pg.display.set_mode(self.screen_dims, pg.FULLSCREEN) if fullscreen else pg.display.set_mode(res)
        pg.display.set_caption("2D RPG")
        self.clock = pg.time.Clock()
        self.tick_counter = 0

        self.map_data = []
        self.nb_row, self.nb_column = 0, 0
        self.cellsize_x, self.cellsize_y = 0, 0

        self.texture_loader = None
        self.dic_textures = {}


    def update_self_to_map(self, level: Map) -> None:

        """ Update les dimensions des cellules """

        self.map_data = level.map_data
        self.nb_row, self.nb_column = level.nb_row, level.nb_column
        self.cellsize_x, self.cellsize_y = level.cellsize_x, level.cellsize_y


    def update(self) -> None:

        """ Update l'écran, le tick global du jeu et les FPS """

        pg.display.flip()
        self.clock.tick(FPS)
        pg.display.set_caption(f"2D RPG : {self.clock.get_fps():.0f} FPS")
        self.tick_counter = (self.tick_counter + 1) % 30


    @staticmethod
    def check_events_and_attack() -> bool:

        """ Capture la sortie du jeu et l'attaque avec "espace" """

        attack = False
        for pg_event in pg.event.get():
            if pg_event.type == pg.QUIT or (pg_event.type == pg.KEYDOWN and pg_event.key == pg.K_ESCAPE):
                pg.quit()
                sysexit()


            if pg_event.type == pg.KEYDOWN and pg_event.key == pg.K_SPACE:
                attack = True

        return attack


    @staticmethod
    def get_moving_player_sprite(player: Player, dic: dict, moving_tic: int) -> pg.surface:

        """ Pour n'importe quel tick, renvoie l'exacte animation de mouvement de link """

        dic_player_costumes = {
            "bas": 201,
            "gauche": 203,
            "haut": 205,
            "droite": 207
        }

        base_direction_costume = dic_player_costumes[player.dir]
        return dic[base_direction_costume + moving_tic]


    @staticmethod
    def get_attack_player_sprite(player: Player, dic: dict, attack_tic: int) -> pg.surface:

        """ Pour n'importe quel tick, renvoie l'exacte animation d'attaque de link """

        player_dir = player.dir
        dic_player_costumes = {
            "bas": 221,
            "gauche": 241,
            "haut": 261,
            "droite": 281
        }

        base_direction_costume = dic_player_costumes[player_dir]
        return dic[base_direction_costume + attack_tic]
    

    @staticmethod
    def create_ennemies_instances(player: Player, dic_ennemy_pos: dict) -> list[DefEnnemy]:

        """ Créé une liste d'instances d'ennemis à partir de leurs positions et types """

        local_liste_ennemies = []
        for ennemy_id in dic_ennemy_pos:
            ennemy_type = dic_ennemy_pos[ennemy_id][0]
            ennemy_cell_coords = (dic_ennemy_pos[ennemy_id][1][0], dic_ennemy_pos[ennemy_id][1][1])

            if ennemy_type.startswith("octorok") or ennemy_type.startswith("leever"):
                type_, color = ennemy_type.split('_')
                if type_ == "octorok":
                    local_liste_ennemies.append(
                        Octorok(player=player, spawning_id=ennemy_id, color=color, cell_coords=ennemy_cell_coords)
                    )
                elif type_ == "leever":
                    local_liste_ennemies.append(
                        Leever(player=player, spawning_id=ennemy_id, color=color, cell_coords=ennemy_cell_coords)
                    )
            elif ennemy_type == "bat":
                local_liste_ennemies.append(
                    Bat(player=player, spawning_id=ennemy_id, cell_coords=ennemy_cell_coords)
                )

        return local_liste_ennemies


    @staticmethod
    def get_ennemy_loot(ennemy_x: float, ennemy_y: float, player) -> Loot:

        """ Renvoir un nombre aléatoire symbolisant le loot que l'adversaire drop """

        if randint(1, 3) == 3: # 1 chance sur 3
            return None
        return Loot(ennemy_x, ennemy_y, player)
    

    def remove_ennemies_from_dic_add_loot(self, current_level_id: int, liste_ennemies: list, player) -> list[Loot]:

        """ Enlève les ennemis du gros dictionnaire de position et créé leur loot (s'il existe) """

        new_loots = []

        # Enlever ennemies mort du dictionnaire et ajoute loot
        for ennemy in liste_ennemies:
            if ennemy.health <= 0:
                pg.mixer.Sound.play(sfx_ennemy_death)
                global_dic_ennemy_nb_positions[current_level_id].pop(ennemy.spawning_ID)
                new_loots.append(self.get_ennemy_loot(ennemy.posx, ennemy.posy, player))

        return [loot for loot in new_loots if loot is not None]


    def check_ennemy_health(self, liste_ennemies: list) -> tuple:

        """ Créer les loots, supprime les ennemis à l'écran et dans le dictionnaire d'ennemies """

        # Enlever ennemies morts de la liste à dessiner
        liste_ennemies = [ennemy for ennemy in liste_ennemies if ennemy.health > 0]

        return liste_ennemies


    def update_ennemies_positions(self, liste_ennemies) -> None:

        """ Update les ennemis en fonction du temps (si tick spécial : recalculer direction au joueur) """

        update_required = self.tick_counter % FPS == 0
        for ennemy in liste_ennemies:
            ennemy.go_to_player(update=update_required)
    

    def update_loot_text(self, liste_loot: list[Loot]) -> None:

        """ Update les costumes des loot en fonction du tick global du jeu """

        for loot in liste_loot:

            if not self.tick_counter % 4 == 0: # Update tous les 4 ticks
                continue

            if loot.loot_type in ["heart_small", "coin_yellow"]:
                if self.tick_counter % 8 == 0:
                    loot.sprite_id = 403 if loot.loot_type == "heart_small" else 411
                else:
                    loot.sprite_id = 404 if loot.loot_type == "heart_small" else 412


    @staticmethod
    def check_key_pressed(current_player_dir: str) -> tuple[bool, str]:

        """ 
        Capture la pressions des touches de mouvements : 
        Renvoie si une touche est pressée, si oui laquelle, et sinon, l'ancienne direction du joueur
        """

        keys = pg.key.get_pressed()
        key_direction_map = {
            pg.K_z: "haut",
            pg.K_s: "bas",
            pg.K_q: "gauche",
            pg.K_d: "droite"
        }

        for key, direction in key_direction_map.items():
            if keys[key]:
                return True, direction, 

        return False, current_player_dir


    def transition_level(
            self, 
            ancient_background: pg.Surface, 
            new_background: pg.Surface, 
            ui: pg.Surface, 
            direction: str, 
            transition_duration: int, 
            px_par_update: int
            ) -> None:
        
        """ Transitionne entre 2 niveaux """
        
        # Longueur totale de la transition
        if direction in ["bas", "haut"]:
            total_size = SCREEN_GAME_HEIGHT

        elif direction in ["droite", "gauche"]:
            total_size = SCREEN_GAME_WIDTH
        else:
            return "MAUVAISE VALEUR DE DIRECTION"

        # De où doit partir l'index 
        if direction in ["bas", "droite"]:
            current_size = total_size
        else:
            current_size = 0

        # Le temps entre chaque frame de transition
        duration_beetween_frames = transition_duration / (total_size / px_par_update) # durée / nb_frames quoi


        if direction == "haut":
            while current_size < total_size: # on part du bas de l'écran
                self.SCREEN.blit(new_background, (0, current_size-total_size + self.screen_ui_dims[1])) # le nouveau a la marque : on le met avant
                self.SCREEN.blit(ancient_background, (0, current_size + self.screen_ui_dims[1]))
                self.SCREEN.blit(ui, (0, 0))
                pg.display.update()
                current_size += px_par_update
                time.sleep(duration_beetween_frames)

        if direction == "gauche":
            while current_size < total_size:
                self.SCREEN.blit(ancient_background, (current_size, self.screen_ui_dims[1]))
                self.SCREEN.blit(new_background, (current_size-total_size, self.screen_ui_dims[1]))
                pg.display.update()
                current_size += px_par_update
                time.sleep(duration_beetween_frames)

        if direction == "bas":
            while current_size > 0:
                self.SCREEN.blit(ancient_background, (0, current_size - total_size + self.screen_ui_dims[1]))
                self.SCREEN.blit(new_background, (0, current_size + self.screen_ui_dims[1]))
                self.SCREEN.blit(ui, (0, 0))
                pg.display.update()
                current_size -= px_par_update
                time.sleep(duration_beetween_frames)  # TODO Un peu unsafe

        if direction == "droite":
            while current_size > 0:
                self.SCREEN.blit(ancient_background, (current_size - total_size, self.screen_ui_dims[1]))
                self.SCREEN.blit(new_background, (current_size, self.screen_ui_dims[1]))
                pg.display.update()
                current_size -= px_par_update
                time.sleep(duration_beetween_frames)


    
    def draw_every_ennemies(self, liste_ennemies: list[DefEnnemy]) -> None:

        """ Dessin des ennemis à l'écran """

        for ennemy in liste_ennemies:
            ennemy_texture_id = ennemy.get_sprite_id(self.tick_counter)
            self.SCREEN.blit(self.dic_textures[ennemy_texture_id], (ennemy.posx, ennemy.posy + self.screen_ui_dims[1]))


    def draw_every_loot(self, liste_loot: list[Loot]) -> None:

        """ Deesin des loots à l'écran"""

        for loot in liste_loot:
            self.SCREEN.blit(self.dic_textures[loot.sprite_id], (loot.posx, loot.posy + self.screen_ui_dims[1]))


    @staticmethod
    def check_collision(x1, y1, w1, h1, x2, y2, w2, h2):

        """ Fonction globale pour checker les collisions """

        return x1 + w1 > x2 and x2 + w2 > x1 and y1 + h1 > y2 and y2 + h2 > y1
    
    



def main():

    pg.mixer.Sound.play(song_overworld)

    """ Init """


    level_changer = LevelMaster()
    current_level_id = level_changer.current_level_ID
    game = Game(res=RES, fullscreen=False)

    # Obligé de définir après le game, sinon pas de video mode
    dic_textures = Textures.load_textures(dic_path=dic_textures_name, texture_size=liste_textures_size,
                                        cell_dims=(CELLSIZE_X, CELLSIZE_Y))
    level = Map(current_level_id)
    game.update_self_to_map(level)
    game.dic_textures = dic_textures

    level_background_cache = level.draw_map_cache(dic_textures=dic_textures)
    player = Player(game=game, dic_textures= dic_textures)
    player_sprite = game.get_moving_player_sprite(player, dic_textures, moving_tic=0)
    player.draw_ui_cache(level_id=current_level_id)
    ennemy_pos = global_dic_ennemy_nb_positions[current_level_id]
    liste_ennemies = game.create_ennemies_instances(player=player, dic_ennemy_pos=ennemy_pos)

    attack_tick_counter = 0
    active_movement = False
    ancienne_dir = player.dir
    player_costume = 0
    scroll_direction = None
    bool_attaque = False
    liste_loots = []

    running = True
    while running:

        """ I/ Joueur """

        # 1) Mouvement brut

        if bool_attaque: # permet de ne pas bouger le joueur si il attaque
            player.attack(liste_ennemies)

        else: 
            bool_attaque = game.check_events_and_attack()
            active_movement, player.dir = game.check_key_pressed(player.dir)

            # Si il y a un changement de direction, on snap
            if player.dir != ancienne_dir:
                ancienne_dir = player.dir
                player.snap_to_grid()

            # Si le joueur se déplace, on précise qu'il n'est plus snappé à la grille
            if active_movement:
                player.snapped_to_grid = False
                scroll_direction = player.move()
        

        # 2) Transition d'écran
                

        if scroll_direction:
            # Changer et dessiner le level
            current_level_id = level_changer.change_level(ancient_level_id=current_level_id,
                                                          scroll_direction=scroll_direction)
            ancient_level = level_background_cache

            level.change_level(new_level_id=current_level_id, game_textures=dic_textures)
            level_background_cache = level.draw_map_cache(dic_textures=dic_textures)

            game.transition_level(ancient_background=ancient_level, 
                                  new_background=level_background_cache,
                                  ui = player.ui_cache,
                                  direction=scroll_direction, transition_duration=1, px_par_update=5)

            game.update_self_to_map(level=level)

            player.update_ui_cache_minimap(level_id=current_level_id)

            #game.update_to_map(level.map_data)
            player.update_to_map()
            
            # Supprimer les loots
            liste_loots = []

            # Changer les ennemies
            ennemy_pos = global_dic_ennemy_nb_positions[current_level_id]
            liste_ennemies = game.create_ennemies_instances(player=player, dic_ennemy_pos=ennemy_pos)

            scroll_direction = None


        # 3) Joueur par rapport aux ennemis et au loot

        if player.invicible:
            if player.tick_invicibility > NB_TICK_PLAYER_INVICIBILITY:
                player.invicible = False
                player.tick_invicibility = 0
            player.tick_invicibility += 1
        
        if liste_loots:
            player.grab_loot(liste_loot=liste_loots)
            game.update_loot_text(liste_loots)


        

        """ II/ Ennemis, Loot """

        # Supprimer les ennemis morts du dictionnaire / créer la liste des nouveaux loots
        new_loots = game.remove_ennemies_from_dic_add_loot(current_level_id, liste_ennemies, player=player)

        # Ajouter le loot des ennemis morts au loot présent
        liste_loots.extend(new_loots)

        # Suprrimer les ennemies morts de l'écran
        liste_ennemies = game.check_ennemy_health(liste_ennemies)

        # Aller au joueur
        game.update_ennemies_positions(liste_ennemies)


        """ III/ Calcul des costumes et render des éléments """

        # Calcul du costume du joueur

        if player.tick_counter > NB_TICKS_TO_UPDATE_PLAYER: # L'animation de "marche" de link
            player_costume = (player_costume + 1) % 2
            player.tick_counter = 0

        if bool_attaque: # 
            player_sprite = game.get_attack_player_sprite(player, dic_textures, attack_tick_counter//2)

            attack_tick_counter += 1
            if attack_tick_counter == 8:
                attack_tick_counter = 0
                bool_attaque = False
                player.play_attack_sfx = True
                player_sprite = game.get_moving_player_sprite(player, dic_textures, player_costume)

        elif active_movement: # La direction de link
            player_sprite = game.get_moving_player_sprite(player, dic_textures, player_costume)


        # 2) Dessin des éléments à l'écran

        game.SCREEN.blit(player.ui_cache, (0, 0))
        game.SCREEN.blit(level_background_cache, (0, game.screen_ui_dims[1]))
        game.draw_every_loot(liste_loot=liste_loots)
        game.draw_every_ennemies(liste_ennemies=liste_ennemies)
        game.SCREEN.blit(player_sprite, (player.posx, player.relative_posy + game.screen_ui_dims[1]))
        game.update()


        player.tick_counter += 1


if __name__ == "__main__":
    main()
