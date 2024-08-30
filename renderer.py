import pygame as pg
from settings import *


""" 
Classe dont le but est de :
- dessiner des choses sur des surfaces 
- dessiner des choses à l'écran
"""


class Renderer:

    def __init__(self, res: tuple, fullscreen: bool) -> None:
        self.SCREEN = pg.display.set_mode(SCREEN_DIMS, pg.FULLSCREEN) if fullscreen else pg.display.set_mode(res)
        pg.display.set_caption("2D RPG")

        self.clock = pg.time.Clock()

        self.dic_textures = {}
        self.tick_counter = 0

        self.level_master = None
    
    
    def transition_into_secret(self, background, ui, player, player_sprite):

        """ Animation quand link entre dans un secret (grotte ou dongeon) """

        if player.dir == "haut":
            for _ in range(10):
                player.posy += 4
                self.SCREEN.fill(BLACK)
                self.SCREEN.blit(ui, (0, 0))
                self.SCREEN.blit(player_sprite, (player.posx, player.posy + SCREEN_UI_DIMS[1]))
                self.SCREEN.blit(background, (0, SCREEN_UI_DIMS[1]))
                pg.display.update()
                pg.mixer.Sound.play(sfx_stairs)
                pg.time.wait(200)
                

    def transition_out_of_secret(self, background, ui, player, player_sprite):

        """ Animation quand link sort dans un secret (grotte ou dongeon) """

        if player.dir == "bas":
            for _ in range(10):
                player.posy -= 4
                self.SCREEN.fill(BLACK)
                self.SCREEN.blit(ui, (0, 0))
                self.SCREEN.blit(player_sprite, (player.posx, player.posy + SCREEN_UI_DIMS[1]))
                self.SCREEN.blit(background, (0, SCREEN_UI_DIMS[1]))
                pg.display.update()
                pg.mixer.Sound.play(sfx_stairs)
                pg.time.wait(200)
                

    def transition_level(
            self, 
            ancient_background: pg.Surface, 
            new_background: pg.Surface, 
            ui: pg.Surface, 
            direction: str, 
            transition_duration: int, 
            px_par_update: int
            ) -> None:
        
        """ Transitionne entre 2 niveaux de l'overworld """
        
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
        duration_beetween_frames = round(transition_duration / (total_size / px_par_update) * 1000) # durée / nb_frames quoi

        if direction == "haut":
            while current_size < total_size: # on part du bas de l'écran
                self.SCREEN.fill(BLACK)
                self.SCREEN.blit(new_background, (0, current_size-total_size + SCREEN_UI_DIMS[1])) # le nouveau a la marque : on le met avant
                self.SCREEN.blit(ancient_background, (0, current_size + SCREEN_UI_DIMS[1]))
                self.SCREEN.blit(ui, (0, 0))
                pg.display.update()
                current_size += px_par_update
                pg.time.wait(duration_beetween_frames)

        if direction == "gauche":
            while current_size < total_size:
                self.SCREEN.fill(BLACK)
                self.SCREEN.blit(ui, (0, 0))
                self.SCREEN.blit(ancient_background, (current_size, SCREEN_UI_DIMS[1]))
                self.SCREEN.blit(new_background, (current_size-total_size, SCREEN_UI_DIMS[1]))
                pg.display.update()
                current_size += px_par_update
                pg.time.wait(duration_beetween_frames)

        if direction == "bas":
            while current_size > 0:
                self.SCREEN.fill(BLACK)
                self.SCREEN.blit(ancient_background, (0, current_size - total_size + SCREEN_UI_DIMS[1]))
                self.SCREEN.blit(new_background, (0, current_size + SCREEN_UI_DIMS[1]))
                self.SCREEN.blit(ui, (0, 0))
                pg.display.update()
                current_size -= px_par_update
                pg.time.wait(duration_beetween_frames)

        if direction == "droite":
            while current_size > 0:
                self.SCREEN.fill(BLACK)
                self.SCREEN.blit(ui, (0, 0))
                self.SCREEN.blit(ancient_background, (current_size - total_size, SCREEN_UI_DIMS[1]))
                self.SCREEN.blit(new_background, (current_size, SCREEN_UI_DIMS[1]))
                pg.display.update()
                current_size -= px_par_update
                pg.time.wait(duration_beetween_frames)

        if not direction:
            print("pas de direction")
        
    @staticmethod
    def visualize():
        """ Fonction de débug pour voir dans quel ordre chaque layer est dessiné """
        pg.time.wait(VISU_TIME * 1000)
        pg.display.update()


    def update(self):
        
        """ Update l'écran, le tick global du jeu et les FPS """

        pg.display.flip()
        self.clock.tick(FPS)
        pg.display.set_caption(f"2D RPG : {self.clock.get_fps():.0f} FPS")

        self.tick_counter = (self.tick_counter + 1) % 30


    def draw_every_ennemies(self, liste_ennemies) -> None:

        """ Dessin des ennemis à l'écran """

        for ennemy in liste_ennemies:
            ennemy_texture_id = ennemy.get_sprite_id(self.tick_counter)
            if ennemy.projectile_thrown:
                self.SCREEN.blit(self.dic_textures[604], (ennemy.projectile.posx, ennemy.projectile.posy + SCREEN_UI_DIMS[1]))
            self.SCREEN.blit(self.dic_textures[ennemy_texture_id], (ennemy.posx, ennemy.posy + SCREEN_UI_DIMS[1]))


    def draw_every_loot(self, liste_loot) -> None:

        """ Deesin des loots à l'écran"""

        for loot in liste_loot:
            self.SCREEN.blit(self.dic_textures[loot.sprite_id], (loot.posx, loot.posy + SCREEN_UI_DIMS[1]))


    def draw_map_cache(self, dic_textures: dict) -> pg.surface:

        """ Dessine une surface de background avec les textures et les actuelles données de la map """

        surface = pg.Surface((SCREEN_GAME_WIDTH, SCREEN_GAME_HEIGHT), pg.SRCALPHA)
        surface.fill((255, 255, 255, 0))

        for row_idx, row_content in enumerate(self.level_master.current_map_data):
            for column_idx, column_content in enumerate(row_content):
                surface.blit(dic_textures[column_content], (column_idx * self.level_master.cell_dims[0], row_idx * self.level_master.cell_dims[1]))
                
        return surface


    def render_on_surface(self, background, liste_loots, liste_ennemies, player_sprite, player_pos) -> pg.Surface:
        
        """ Dessine la zone de jeu entière sur une surface (PAS A L'ECRAN) """

        surface = pg.Surface(SCREEN_GAME_DIMS, pg.SRCALPHA)
        
        surface.blit(background, (0, 0))
        
        for ennemy in liste_ennemies:
            ennemy_texture_id = ennemy.get_sprite_id(self.tick_counter)
            surface.blit(self.dic_textures[ennemy_texture_id], (ennemy.posx, ennemy.posy))

        for loot in liste_loots:
            surface.blit(self.dic_textures[loot.sprite_id], (loot.posx, loot.posy))
        
        surface.blit(player_sprite, (player_pos[0], player_pos[1]))

        return surface
        

    def render_on_screen(self, ui, background, liste_loots, liste_ennemies, player_sprite, player_pos, weapon_sprite, weapon_pos):
        
        """ Dessine la zone de jeu entière sur l'écran """

        self.SCREEN.fill(BLACK)
        self.SCREEN.blit(ui, (0, 0))
        self.SCREEN.blit(background, (0, SCREEN_UI_DIMS[1]))
        self.draw_every_loot(liste_loot=liste_loots)
        self.draw_every_ennemies(liste_ennemies=liste_ennemies)
        if weapon_sprite:
            self.SCREEN.blit(weapon_sprite, (weapon_pos[0], weapon_pos[1] + SCREEN_UI_DIMS[1]))
        self.SCREEN.blit(player_sprite, (player_pos[0], player_pos[1] + SCREEN_UI_DIMS[1]))
