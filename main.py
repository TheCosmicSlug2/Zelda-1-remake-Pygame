import textures
from player import Player
from level_master import *
from settings import *
from ennemy import DefEnnemy, Bat, Octorok, Leever
from renderer import Renderer
from physics import Physics
from loot import Loot
from random import choice, randint


# Module pour détecter oprimisations possibles
# from profilehooks import profile


"""
Fichier contenant:
- la classe "Game" (un peu un fourre-tout de fonction qui gèrent l'état du jeu)
- la boucle principale de jeu
"""


"""
INFOS POUR COMPRENDRE TOUT CA :

La boucle de jeu est divisée en 5 parties :
- Capture des événements claviers (avec la classe "Game" de main.py)
- Déplacement du joueur selon les touches pressées (avec la classe "Player" de player.py)
- Transition d'écran possible si le joueur touche un bord
- Déplacement des ennemis
- Render de tout
"""

class Game:
    def __init__(self, level_master: LevelMaster) -> None:

        self.level_master = level_master
        self.tick_counter = 0
        self.texture_loader = None

        self.current_background = None
        self.liste_ennemies = []
        self.liste_loots = []

        self.hold_memory_ennemies = []
        self.hold_memory_loots = []


    @staticmethod
    def check_events_and_attack() -> bool:

        """ Capture le quittage du jeu par l'user et l'attaque du joueur s'il utilise la touche "espace" """

        game_running = True

        attack = False
        for pg_event in pg.event.get():
            if pg_event.type == pg.QUIT or (pg_event.type == pg.KEYDOWN and pg_event.key == pg.K_ESCAPE):
                game_running = False


            if pg_event.type == pg.KEYDOWN and pg_event.key == pg.K_SPACE:
                attack = True

        return attack, game_running
    

    def create_ennemies_instances(self, player: Player) -> list[DefEnnemy]:

        """ 
        Créé une liste d'instances d'ennemis selon le niveau à partir de leurs positions et types 
        Chaque ennemi est défini en fonction du joueur, pour qu'il connaisse sa position et voit s'il le touche
        """

        self.liste_ennemies = []
        for ennemy_id, ennemy_data in self.level_master.current_ennemy_positions.items():
            ennemy_type = ennemy_data[0]
            ennemy_cell_coords = (ennemy_data[1][0], ennemy_data[1][1])

            if ennemy_type.startswith("octorok") or ennemy_type.startswith("leever"):
                type_, color = ennemy_type.split('_')
                str_speed = choice(["slow", "fast"])
                if type_ == "octorok":
                    self.liste_ennemies.append(
                        Octorok(player=player, level_master=self.level_master, spawning_id=ennemy_id, color=color, cell_coords=ennemy_cell_coords, speed=str_speed)
                    )
                elif type_ == "leever":
                    self.liste_ennemies.append(
                        Leever(player=player, level_master=self.level_master, spawning_id=ennemy_id, color=color, cell_coords=ennemy_cell_coords, speed=str_speed)
                    )
            elif ennemy_type == "bat":
                self.liste_ennemies.append(
                    Bat(player=player, level_master=self.level_master, spawning_id=ennemy_id, cell_coords=ennemy_cell_coords)
                )


    @staticmethod
    def get_ennemy_loot(ennemy_x: float, ennemy_y: float, player) -> Loot:

        """ Renvoir un nombre aléatoire symbolisant le loot que l'adversaire drop """

        if randint(1, 3) == 3: # 1 chance sur 3 de ne rien faire tomber
            return None
        return Loot(ennemy_x, ennemy_y, player)
    

    def remove_ennemies_from_dic_add_loot(self, player) -> list[Loot]:

        """ Enlève les ennemis du gros dictionnaire de positions d'ennemis et créé leur loot (si cet ennemi en drop un) """

        new_loots = []

        # Enlever ennemies mort du dictionnaire et ajoute loot
        for ennemy in self.liste_ennemies:
            if ennemy.health <= 0:
                pg.mixer.Sound.play(sfx_ennemy_death)
                global_dic_ennemy_nb_positions[self.level_master.current_level_ID].pop(ennemy.spawning_ID)
                new_loots.append(self.get_ennemy_loot(ennemy.posx, ennemy.posy, player))

        self.liste_loots.extend([loot for loot in new_loots if loot is not None])


    def check_ennemy_health(self) -> tuple:

        """ Supprime les ennemis morts de la liste, signifiants qu'ils ne seront pas dessinés à l'écran """

        # Enlever ennemies morts de la liste à dessiner
        self.liste_ennemies = [ennemy for ennemy in self.liste_ennemies if ennemy.health > 0]


    def update_ennemies_positions(self) -> None:

        """ Update les ennemis en fonction du temps (si tick spécial : recalculer direction au joueur) """

        update_required = self.tick_counter % FPS == 0
        for ennemy in self.liste_ennemies:
            ennemy.do_something(update=update_required)
    

    def update_loot_text(self) -> None:

        """ Update (fait "osciller") les costumes des loot en fonction du tick global du jeu """

        for loot in self.liste_loots:

            if not self.tick_counter % 4 == 0: # Update tous les 4 ticks
                continue

            if loot.type in ["heart_small", "coin_yellow"]:
                if self.tick_counter % 8 == 0:
                    loot.sprite_id = 403 if loot.type == "heart_small" else 411
                else:
                    loot.sprite_id = 404 if loot.type == "heart_small" else 412


    @staticmethod
    def check_key_pressed(current_player_dir: str) -> tuple[bool, str]:

        """ 
        Capture la pressions des touches de mouvements : 
        Renvoie si une touche est pressée, si oui laquelle, et sinon, l'ancienne direction du joueur
        """

        keys = pg.key.get_pressed()
        key_direction_map = {
            pg.K_UP: "haut",
            pg.K_DOWN: "bas",
            pg.K_LEFT: "gauche",
            pg.K_RIGHT: "droite"
        }

        for key, direction in key_direction_map.items():
            if keys[key]:
                return True, direction, 

        return False, current_player_dir


    def transition_beetween_levels(self, level_master, renderer, player, player_sprite, dic_textures):
        
        """ 
        Fonction pour la transition artistique entre chaque niveau :
        3 étapes : 
        - Changer les données du niveau que possède "level_master"
        - Dessiner le nouveau niveau dans une variable
        - Effectuer la transition à partir de l'ancien niveau et du nouveau (différentes transitions si le joueur entre dans une cave/dongeon)
        - Créé les ennemis du nouveau niveau / ajuste la position du joueur
        """

        # Changer et dessiner le level
        level_master.change_level(scroll_direction=player.current_level_transition)

        # On peut changer ça à tout moment par
        # ancient_level = current_background
        ancient_level = renderer.render_on_surface(
            background=self.current_background,
            liste_loots=self.liste_loots,
            liste_ennemies=self.liste_ennemies,
            player_sprite=player_sprite,
            player_pos=(player.posx, player.posy)
        )

        if player.current_level_transition == "get_in_secret":
            renderer.transition_into_secret(
                background=self.current_background,
                ui = player.ui_cache,
                player=player,
                player_sprite=player_sprite
            )
            self.current_background = renderer.draw_map_cache(dic_textures=dic_textures)
            player.adjust_pos_to_get_into_secret()

        if player.current_level_transition == "get_out_secret":
            self.current_background = renderer.draw_map_cache(dic_textures=dic_textures)
            player.adjust_pos_to_get_out_of_secret()
            renderer.transition_out_of_secret(
                background=self.current_background,
                ui=player.ui_cache,
                player=player,
                player_sprite=player_sprite
            )
        else:
            self.current_background = renderer.draw_map_cache(dic_textures=dic_textures)
            renderer.transition_level(ancient_background=ancient_level, 
                                    new_background=self.current_background,
                                    ui = player.ui_cache,
                                    direction=player.current_level_transition, 
                                    transition_duration=1, 
                                    px_par_update=5
            )
        
        
            player.adjust_pos_to_scrollage(player.current_level_transition)

        if player.current_level_transition == "get_in_secret":
            if level_master.current_level_ID < 201:
                level_master.current_world_type = "cavern"
            else:
                level_master.current_world_type = "dungeon"
        elif player.current_level_transition == "get_out_secret":
            level_master.current_world_type = "overworld"
        else:
            player.update_ui_cache_minimap()


        # Supprimer les loots
        self.liste_loots = []

        # Changer les ennemies
        self.create_ennemies_instances(player=player)


        player.triggered_level_transition = False
        player.current_level_transition = None

    
#@profile(stdout=False, filename='g.prof')  # <== Profiling

def main():

    pg.mixer.Sound.play(song_overworld, loops=-1) # "-1" -> Boucle infiniment

    """ Init/Préprocessing """

    # La classe qui gère l'écran/le renderage...
    renderer = Renderer(res=RES, fullscreen=False)

    # Classe pour la physique des objets
    physics = Physics()
    

    # Dictionnaire de toutes les textures, sous la forme : {idx-de-la-texture: texture}
    dic_textures = textures.load_textures(
        dic_path=dic_textures_name, 
        texture_size=liste_textures_size,
        cell_dims=(CELLSIZE_X, CELLSIZE_Y)
    )
    renderer.dic_textures = dic_textures
    
    # Classe possédant toutes les données du niveau actuel/ dimensions des cellules/ nb de colomnes et lignes...
    # Tous les objets du jeu possèdent une instance de cette classe parce qu'elle est putain d'importante
    level_master = LevelMaster()

    # C'est moche de l'initialiser comme ça mais flemme
    renderer.level_master = level_master

    # Classe principale
    game = Game(level_master=level_master)

    # Premier "fond d'écran de jeu" que le joueur verra
    game.current_background = renderer.draw_map_cache(dic_textures=dic_textures)

    # Joueur
    player = Player(level_master=level_master, dic_textures=dic_textures)
    player_sprite = player.get_moving_sprite(moving_tic=0)
    player.draw_ui_cache() # "ui", c'est ce qu'il y a en haut de l'écran
    
    # Ennemies de l'écran actuel
    game.create_ennemies_instances(player=player)

    # Arme du joueur
    weapon_sprite = None
    weapon_pos = None

    # Le joueur possède 2 directions : l'actuelle et l'ancienne, pour savoir si sa direction a changé et pour pouvoir le "snapper" à la grille
    ancienne_dir = player.dir
    player_costume = 0


    # Boucle principale de jeu
    game_running = True
    while game_running:

        """ I/ Joueur """

        # 1) Mouvement du joueur

        if player.is_attacking: # permet de ne pas bouger le joueur s'il attaque
            player.attack(game.liste_ennemies)
        else: 
            player.is_attacking, game_running = game.check_events_and_attack()
            player.is_moving, player.dir = game.check_key_pressed(current_player_dir=player.dir)

            # Si il y a un changement de direction, on snap à la grille
            if player.dir != ancienne_dir:
                ancienne_dir = player.dir
                player.snap_to_grid()

            # On laisse ensuite le joueur se déplacer
            if player.is_moving:
                player.move()

        if level_master.current_secret_exist: # S'il y a un "secret" dans le niveau actuel
            if physics.is_touching_secret( # On checke si le joueur touche le secret. 
                # J'ai créé un 2ème "if" afin de ne pas avoir à checker les 2 conditions avec "and": calculer si le joueur touche le secret demande des caluls et il ne faudrait pas le faire si le secret n'existe pas au préalable
                (player.posx, player.posy),
                PLAYER_DIMS,
                player.dir,
                level_master.current_secret_position,
                level_master.cell_dims
            ):
                player.snap_to_grid() # Si c'est le cas, on snap le joueur et change des variables pour dire qu'il y a une transition d'écran
                player.current_level_transition = "get_in_secret"
                player.triggered_level_transition = True
                level_master.current_world_type = "cavern"

        # 2) Transition d'écran                

        if player.triggered_level_transition:
            game.transition_beetween_levels(
                level_master=level_master,
                renderer=renderer,
                player=player,
                player_sprite=player_sprite,
                dic_textures=dic_textures
            )
            player.triggered_level_transition = False
            

        # 3) Réaction du joueur par rapport aux ennemis et au loot

        if player.invicible:
            # Si le joueur est invincible, on augmente un compteur jusqu'à un certain point, puis on enlève l'invincibilité
            player.tick_invicibility += 1
            if player.tick_invicibility > NB_TICK_PLAYER_INVICIBILITY:
                player.invicible = False
                player.tick_invicibility =  0
            
        
        if game.liste_loots: 
            # S'il y a des loots à l'écran : on checke si le joueur en a attrapé un, et on update les costumes des loots
            player.grab_loot(liste_loot=game.liste_loots)
            game.update_loot_text()

        

        """ II/ Ennemis, Loot """

        # Supprimer les ennemis morts du dictionnaire / Ajoute les loots droppés
        game.remove_ennemies_from_dic_add_loot(player=player)

        # Suprrimer les ennemies morts de l'écran
        game.check_ennemy_health()

        # Update les positions des ennemies
        game.update_ennemies_positions()


        """ III/ Calcul des costumes de chaque élément et render des éléments """

        # Calcul du costume du joueur

        if player.tick_counter > NB_TICKS_TO_UPDATE_PLAYER: # L'animation de "marche" de link
            player_costume = (player_costume + 1) % 2
            player.tick_counter = 0

        if player.is_attacking: 
            # Si le joueur attaque, on cherche le costume de tous les éléments de son animation d'attaque
            player_sprite = player.get_attack_sprite(player.tick_attack//2)
            weapon_sprite = player.get_weapon_sprite()
            weapon_pos = player.get_weapon_position(player.tick_attack)

            player.tick_attack += 1
            if player.tick_attack == 8:
                player.tick_attack = 0
                player.is_attacking = False
                player.play_attack_sfx = True
                weapon_sprite = None
                player_sprite = player.get_moving_sprite(player_costume)

        elif player.is_moving or player.invicible:
            player_sprite = player.get_moving_sprite(player_costume)


        # 2) Dessin des éléments à l'écran

        renderer.render_on_screen(
            ui=player.ui_cache,
            background=game.current_background,
            liste_loots=game.liste_loots,
            liste_ennemies=game.liste_ennemies,
            player_sprite=player_sprite,
            player_pos=(player.posx, player.posy),
            weapon_sprite=weapon_sprite,
            weapon_pos=weapon_pos
        )


        # Update le display
        renderer.update()

        game.tick_counter = (game.tick_counter + 1) % 30

        player.tick_counter += 1


if __name__ == "__main__":
    main()
    
