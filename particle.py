from settings import *
from entity import Entity
from physics import Physics
from settings import * 


"""
Classe de particule / Les "rocher" que les poulpes tirent
"""


class Particle(Entity):
    def __init__(self, posx, posy) -> None:
        super.__init__()
        self.posx = posx
        self.posy = posy
        self.speed = 10


class DeathCloud(Particle):
    def __init__(self, posx, posy, dic_textures) -> None:
        super().__init__(posx, posy)

        self.tick = 0
        self.dic_textures = dic_textures

class Projectile:
    def __init__(self, player) -> None:
        self.player = player
        self.dims = (20, 20)
        self.physics = Physics()
        self.speed = 10

    
    def init_to_ennemy(self, posx, posy, direction):
        self.posx = posx
        self.posy = posy
        self.dir = direction

        delta_dir = self.physics.dic_dir_to_movement[self.dir]
        self.delta_speed = (delta_dir[0] * self.speed, delta_dir[1] * self.speed)
    
    def check_touch_border(self):
        return self.physics.get_is_touching_screen_border(SCREEN_GAME_DIMS, (self.posx, self.posy), self.dims)

    def move(self):
        self.posx += self.delta_speed[0]
        self.posy += self.delta_speed[1]
    
    def check_for_player_collision(self):
        return self.physics.check_collision(self.posx, self.posy, self.dims[0], self.dims[1], self.player.posx, self.player.posy, self.player.width, self.player.height)

    
    

        
