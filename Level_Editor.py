import pygame as pg
import textures
import game_data


"""
Meilleur Editeur Du Monde
"""


class LevelEditorSettings:
    def __init__(self) -> None:

        """ Ecran """
        self.screen_dims = (600, 400)
        self.level_dims = (16, 11)
        self.cell_dims = (int(self.screen_dims[0] / self.level_dims[0]), int(self.screen_dims[1] / self.level_dims[1]))
        self.screen_dims = (self.level_dims[0] * self.cell_dims[0], self.level_dims[1] * self.cell_dims[1])

        """ Level / Editeur """
        self.base_texture_idx = 0
        self.FPS = 30

        """ Couleur """
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.LIGHT_BLACK = (60, 60, 60)
        self.PINK = (255, 130, 255)
        self.TRANSPARENT_WHITE = (255, 255, 255, 200)

        """ Fonts """
        self.font_path = "ressources/fonts/zelda_original.ttf"

        self.small_instructions_dims = (160, 20)
        self.big_instructions_dims = (400, 240)

        self.text_height_small = 8
        self.font_small_instructions = pg.font.Font(self.font_path, self.text_height_small)
        self.text_height_big = 8
        self.font_big_instructions = pg.font.Font(self.font_path, self.text_height_big)
        self.text_height_name = 9
        self.font_texture_name = pg.font.Font(self.font_path, self.text_height_name)
        self.text_grid_height = 10
        self.font_grid = pg.font.Font(self.font_path, 10)        


class Utils(LevelEditorSettings):
    def __init__(self) -> None:
        pass

    def print_formatted_list(self, level_name, level_dims, level_data):
        print(f"\n\nLEVEL {level_name} ({level_dims[0]}x{level_dims[1]}) : \n\n\n")
        print("[")
        for row_content in level_data:
            print(row_content, end=",\n")
        print("]")


class TickMaster:
    def __init__(self) -> None:
        self.dic_tick = {
            "global": 0,
            "inventory_update": 0,
            "grid_update": 0,
            "instructions_update": 0
        }

    def update(self):
        for tick_name in self.dic_tick:
            self.dic_tick[tick_name] += 1


class StateMaster:
    def __init__(self) -> None:
        self.grid_shown = False
        self.inventory_shown = False
        self.instructions_shown = False
        self.ref_idx = 0
        

class DataMaster(LevelEditorSettings):
    def __init__(self, dic_textures) -> None:
        super().__init__()
        self.level_data = self.get_level_list()
        self.translation_dic = self.get_translation_dic(dic_textures)
        self.current_idx = 0
        self.current_texture_idx = self.translation_dic[self.current_idx]
        self.current_level_name = "\"No level Name\""
    

    def get_level_list(self):
        return [[self.base_texture_idx for _ in range(self.level_dims[0])] for _ in range(self.level_dims[1])]
    
    def change_one_element_in_list(self, texture_idx, grid_pos):
        self.level_data[grid_pos[1]][grid_pos[0]] = texture_idx
    
    def get_translation_dic(self, dic_textures):
        texture_keys = list(dic_textures.keys())
        return {translated_idx: key for translated_idx, key in enumerate(texture_keys)}
    
    def reset_level_list(self):
        self.level_data = self.get_level_list()

    def set_idx_from_inventory_mouse_pos(self, mouse_pos, current_inventory_content):
        keys = list(current_inventory_content.keys())
        values = list(current_inventory_content.values())
        current_mouse_idx = mouse_pos[1] * self.level_dims[0] + mouse_pos[0]
        
        if current_mouse_idx > len(values):
            current_mouse_idx = len(values) - 1

        # On a la position de la cellule dans la grille
        # A partir de ça, on peut avoir l'id général avec la liste des clés de inventory content
        # On trouve l'id de la texture en traduisant l'id général

        self.current_idx = current_inventory_content[keys[current_mouse_idx]]
        self.current_texture_idx = self.translation_dic[self.current_idx]
    
    def change_current_idx(self, amount):
        self.current_idx += amount
        self.current_idx = self.current_idx % (len(self.translation_dic) - 1)
        self.current_texture_idx = self.translation_dic[self.current_idx]
        


class Renderer(LevelEditorSettings):
    def __init__(self) -> None:
        super().__init__()
        self.SCREEN = pg.display.set_mode(self.screen_dims)
        pg.display.set_caption("- Level Editor -")
        self.clock = pg.time.Clock()
        self.dic_textures = {}
        self.current_inventory_idx = 0
    
    def render_all(self, data_master):
        self.render_background_debug()
        self.render_full_level_on_surface(data_master.level_data)
        self.render_inventory(data_master.translation_dic)
        self.render_big_instructions()
        self.render_small_instructions()
        self.render_texture_under_mouse(data_master.current_idx)
        self.render_texture_name(
                data_master.current_texture_idx, 
                game_data.dic_textures_name[data_master.current_texture_idx]
        )
        self.render_grid()

    def render_background_debug(self):
        self.background_debug = pg.Surface(self.screen_dims)
        self.background_debug.fill(self.PINK)
        rect_dims = (self.cell_dims[0] / 2, self.cell_dims[1] / 2)
        for row_idx in range(self.level_dims[1] * 2): # 2x plus car le rectangle est 2x moins grand que la cellule
            for column_idx in range(self.level_dims[0] * 2):
                if (column_idx + row_idx) % 2 == 0:
                    rect = pg.Rect(column_idx * rect_dims[0], row_idx * rect_dims[1], rect_dims[0], rect_dims[1])
                    pg.draw.rect(self.background_debug, self.LIGHT_BLACK, rect)

    def render_full_level_on_surface(self, level_data):
        self.level_surface = pg.Surface(self.screen_dims)
        self.level_surface.blit(self.background_debug, (0, 0))
        for row_idx, row_content in enumerate(level_data):
            for column_idx, column_content in enumerate(row_content):
                if column_content == 0: # Transparence
                    continue
                self.level_surface.blit(
                    self.dic_textures[column_content], 
                    (column_idx * self.cell_dims[0], row_idx * self.cell_dims[1])
                )

    def change_one_texture_on_surface(self, texture_idx, grid_pos):
        texture = self.dic_textures[texture_idx]
        texture_pos = (grid_pos[0] * self.cell_dims[0], grid_pos[1] * self.cell_dims[1])
        self.level_surface.blit(texture, texture_pos)

    def render_inventory(self, translation_dic):
        self.inventory_idx = 0
        self.inventory_texture_dic = {}
        self.inventory_content_dic = {}
        last_idx = 0
        dummy_idx = 0

        # Créer un dictionnaire de débug
        inverted_translation_dic = {}
        for key, value in translation_dic.items():
            inverted_translation_dic[value] = key

        for max_texture_idx in [50, 200, 300, 400, 500, 600, 700, 1000]:
            surface = pg.Surface(self.screen_dims)
            surface.blit(self.background_debug, (0, 0))
            textures_a_blitter = [value for key, value in self.dic_textures.items() if key >= last_idx and key < max_texture_idx]
            self.inventory_content_dic[dummy_idx] = {key: value for key, value in inverted_translation_dic.items() if key >= last_idx and key < max_texture_idx}
            

            for value_idx, value in enumerate(textures_a_blitter):
                column_value = value_idx % self.level_dims[0]
                row_value = value_idx // self.level_dims[0]
                surface.blit(value, (column_value * self.cell_dims[0], row_value * self.cell_dims[1]))
            
            self.inventory_texture_dic[dummy_idx] = surface

            last_idx = max_texture_idx
            dummy_idx += 1
        self.inventory_content_dic[7] = {1001: 189, 1002: 190, 1003: 191}
    
    def render_small_instructions(self):
        ecart_x = 5
        ecart_y = 2

        self.small_instructions = pg.Surface(self.small_instructions_dims, pg.SRCALPHA)
        self.small_instructions.fill(self.TRANSPARENT_WHITE)
        instructions_text = [
            "\"s\" : instructions"
        ]

        text_content = instructions_text[0]
        text_drawn = self.font_small_instructions.render(text_content, True, self.BLACK)
        self.small_instructions.blit(text_drawn, (ecart_x, self.text_height_small + ecart_y))

    def render_big_instructions(self):

        ecart_y = 5

        self.big_instructions = pg.Surface(self.big_instructions_dims, pg.SRCALPHA) # Pas de transparence = MONTRER
        self.big_instructions.fill(self.TRANSPARENT_WHITE)
        instructions_text = [
            "Instructions : ",
            "",
            "=> SOURIS : ",
            "molette haut : texture suivante",
            "molette bas : texture precedente",
            "click gauche : appliquer la texture",
            "click droit : ouvrir/fermer inventaire textures",
            "",
            "=> CLAVIER :",
            "\"d\" : effacer tout",
            "\"g\" : montrer la grille",
            "\"p\" : afficher les donnees du niveau",
            "\"q\" : quitter l'editeur",
            "\"s\" : cacher les instructions",
            "\"l\" : importer un niveau dans l'editeur"
        ]

        text_idx = 0
        for text_content in instructions_text:
            text_drawn = self.font_small_instructions.render(text_content, True, self.BLACK)
            self.big_instructions.blit(text_drawn, (20, 20 + text_idx * (self.text_height_big + ecart_y)))
            text_idx += 1


    def render_texture_under_mouse(self, texture_idx):
        self.texture_under_mouse = self.dic_textures[texture_idx]

    def render_texture_name(self, text_id, text_name):
        
        ecart = (5, 2)

        text = self.font_texture_name.render(f"{text_id}: {text_name}", True, self.BLACK)
        self.texture_name = pg.Surface((text.get_width() + ecart[0] * 2, text.get_height() + ecart[1] * 2), pg.SRCALPHA)
        self.texture_name.fill(self.TRANSPARENT_WHITE)
        self.texture_name.blit(text, ecart)

    def render_grid(self):
        self.grid = pg.Surface(self.screen_dims, pg.SRCALPHA)
        ecart_nb_to_grid = 5
        nb = 1

        # Dessiner les lignes verticales
        for x in range(0, self.screen_dims[0], self.cell_dims[0]):
            column_num = self.font_grid.render(str(nb), True, self.BLACK)
            pg.draw.line(self.grid, (0, 0, 0, 255), (x, 0), (x, self.screen_dims[1]), 2)
            self.grid.blit(column_num, (x + ecart_nb_to_grid, ecart_nb_to_grid))
            nb += 1
        # dessine une ligne verticale à droite
        pg.draw.line(self.grid, (0, 0, 0, 255), (self.screen_dims[0]-2, 0), (self.screen_dims[0]-2, self.screen_dims[1]), 2)

        nb = 1

        # Dessiner les lignes horizontales
        for y in range(0, self.screen_dims[1], self.cell_dims[1]):
            row_num = self.font_grid.render(str(nb), True, self.BLACK)
            pg.draw.line(self.grid, (0, 0, 0, 255), (0, y), (self.screen_dims[0], y), 2)
            self.grid.blit(row_num, (ecart_nb_to_grid, y + ecart_nb_to_grid))
            nb += 1
        # dessine une ligne horizontale en bas
        pg.draw.line(self.grid, (0, 0, 0, 255), (0, self.screen_dims[1]-2), (self.screen_dims[0], self.screen_dims[1]-2), 2)

    def display_inventory(self):
        self.SCREEN.blit(self.inventory_texture_dic[self.current_inventory_idx], (0, 0))
        pg.display.update()


    def display_on_screen(self, mouse_pos, show_grid, show_instructions):
        self.SCREEN.blit(self.level_surface, (0, 0)) 

        # La texture à la souris
        self.SCREEN.blit(self.texture_under_mouse, mouse_pos)

        # La grille
        if show_grid: 
            self.SCREEN.blit(self.grid, (0, 0))

        # Les instructions
        if show_instructions:
            self.SCREEN.blit(
                self.big_instructions, 
                (
                    self.screen_dims[0] - self.big_instructions_dims[0], 
                    self.screen_dims[1] - self.big_instructions_dims[1]
                )
            )

        else:
            self.SCREEN.blit(
                self.small_instructions, 
                (
                    self.screen_dims[0] - self.small_instructions_dims[0], 
                    self.screen_dims[1] - self.small_instructions_dims[1]
                )
            )

        # Les propriétés à la souris
        self.SCREEN.blit(self.texture_name, (mouse_pos[0] + self.cell_dims[0], mouse_pos[1] + self.cell_dims[1]))

    def update(self):
        pg.display.flip()
        self.clock.tick(self.FPS)


class InputHandler(LevelEditorSettings):
    def __init__(self) -> None:
        super().__init__()
        self.left_click_down = False

    def get_mouse_events(self):

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "quit_editor"
            
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.left_click_down = True
                return "left_click"

            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self.left_click_down = False

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                return "right_click"
            
            if event.type == pg.MOUSEWHEEL and event.y > 0:
                return "wheel_up"
            
            if event.type == pg.MOUSEWHEEL and event.y < 0:
                return "wheel_down"
        
        return None
    
    @staticmethod
    def get_keyboard_events():

        pg_keys_to_str = {
            pg.K_d: "d",
            pg.K_g: "g",
            pg.K_p: "p",
            pg.K_q: "q",
            pg.K_s: "s",
            pg.K_l: "l"
        }
        pg_keys = pg_keys_to_str.keys()

        keys = pg.key.get_pressed()

        # Renvoie une seule touche à la fois
        for possible_pressed_key in pg_keys:
            if keys[possible_pressed_key]:
                return pg_keys_to_str[possible_pressed_key]
    
    def get_mouse_pos(self):
        return pg.mouse.get_pos()

    def get_mouse_pos_in_grid(self):
        mouse_pos = pg.mouse.get_pos()
        mouse_cell_x = int(mouse_pos[0] // self.cell_dims[0])
        mouse_cell_y = int(mouse_pos[1] // self.cell_dims[1])
        return mouse_cell_x, mouse_cell_y
    
    def get_mouse_pos_snapped(self):
        mouse_x, mouse_y = self.get_mouse_pos_in_grid()
        return mouse_x * self.cell_dims[0], mouse_y * self.cell_dims[1]



def main():
    pg.init()
    pg.font.init()

    level_editor_settings = LevelEditorSettings()
    renderer = Renderer()

    dic_textures = textures.load_textures(
        game_data.dic_textures_name,
        game_data.liste_textures_size,
        level_editor_settings.cell_dims
    )

    renderer.dic_textures = dic_textures

    data_master = DataMaster(dic_textures)

    renderer.render_all(data_master)
    
    input_handler = InputHandler()
    utils = Utils()

    tick_master = TickMaster()
    state_master = StateMaster()

    editor_running = True
    while editor_running:
        mouse_event = input_handler.get_mouse_events()

        if mouse_event == "quit_editor":
            editor_running = False
        
        if input_handler.left_click_down:
            mouse_pos = input_handler.get_mouse_pos_in_grid()
            data_master.change_one_element_in_list(data_master.current_texture_idx, mouse_pos)
            renderer.change_one_texture_on_surface(data_master.current_texture_idx, mouse_pos)
        
        if mouse_event == "right_click":
            renderer.display_inventory()
            inventory_shown = True
            while inventory_shown:
                mouse_event = input_handler.get_mouse_events()
                if mouse_event == "quit_editor":
                    inventory_shown = False
                    editor_running = False
                
                if mouse_event == "wheel_up":
                    renderer.current_inventory_idx = (renderer.current_inventory_idx + 1) % (len(renderer.inventory_texture_dic) - 1)
                    # ajouter 1 au background inventaire du renderer
                    renderer.display_inventory()
                
                if mouse_event == "wheel_down":
                    # enlever 1 au background inventaire du renderer
                    renderer.current_inventory_idx = (renderer.current_inventory_idx - 1) % (len(renderer.inventory_texture_dic) - 1)
                    renderer.display_inventory()
                
                if mouse_event == "left_click" or mouse_event == "right_click":
                    mouse_pos = input_handler.get_mouse_pos_in_grid()
                    texture_names_in_current_inventory = renderer.inventory_content_dic[renderer.current_inventory_idx]
                    data_master.set_idx_from_inventory_mouse_pos(mouse_pos, texture_names_in_current_inventory)
                    inventory_shown = False
        
        if mouse_event == "wheel_up":
            data_master.change_current_idx(1)
        
        if mouse_event == "wheel_down":
            data_master.change_current_idx(-1)

        keyboard_event = input_handler.get_keyboard_events()

        if keyboard_event == "p":
            utils.print_formatted_list(data_master.current_level_name, data_master.level_dims, data_master.level_data)
        
        if keyboard_event == "d":
            data_master.reset_level_list()
            renderer.render_full_level_on_surface(data_master.level_data)
        
        if keyboard_event == "g" and tick_master.dic_tick["grid_update"] > 3:
            state_master.grid_shown = not state_master.grid_shown
            tick_master.dic_tick["grid_update"] = 0
        
        if keyboard_event == "q":
            editor_running = False
        
        if keyboard_event == "s" and tick_master.dic_tick["instructions_update"] > 5:
            state_master.instructions_shown = not state_master.instructions_shown
            tick_master.dic_tick["instructions_update"] = 0

        if keyboard_event == "l":
            data_master.current_level_name = int(input("\n\nEntrez l'ID du niveau : \n >> "))
            data_master.level_data = game_data.dic_world[data_master.current_level_name]
            renderer.render_full_level_on_surface(data_master.level_data)

        
        if data_master.current_idx != state_master.ref_idx:
            renderer.render_texture_under_mouse(data_master.current_texture_idx)
            renderer.render_texture_name(
                data_master.current_texture_idx, 
                game_data.dic_textures_name[data_master.current_texture_idx]
            )
            state_master.ref_idx = data_master.current_idx
        

        mouse_pos = input_handler.get_mouse_pos_snapped()


        if tick_master.dic_tick["global"] > renderer.FPS * 5:
            tick_master.dic_tick["global"] = 0
            renderer.render_full_level_on_surface(data_master.level_data)

        renderer.display_on_screen(
            mouse_pos, 
            state_master.grid_shown, 
            state_master.instructions_shown
        )

        renderer.update()
        
        tick_master.update()

if __name__ == "__main__":
    main()


# Ptite musique de fond ?
# Ajouter ennemies
# Ajouter nom des catégories d'inventaire

