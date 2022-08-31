from email.mime import image
from turtle import update
from matplotlib import animation
import pygame
import constants as const
import helpers as h


class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)

        self.sprite_type = 'weapon'
        self.damage = 20

        self.direction = player.direction
        self.last_direction = player.last_direction

        # Graphic
        graphics_path = 'graphics/weapon/'
        self.animations = h.import_folder(graphics_path+player.last_direction, normalize=False)
        self.image = self.animations[0]
        self.animation_speed = 0.20
        self.frame_index = 0


        # Placement
        if self.last_direction == 'right':
            self.rect = self.image.get_rect(midleft = player.rect.midright+pygame.Vector2(-35,10) )
        elif self.last_direction == 'left':
            self.rect = self.image.get_rect(midright = player.rect.midleft+pygame.Vector2(35,10))
        elif self.last_direction == 'down':
            self.rect = self.image.get_rect(midtop = player.rect.midbottom+pygame.Vector2(0,-35))
        else:
            self.rect = self.image.get_rect(midbottom = player.rect.midtop+pygame.Vector2(0,35))

    def animate(self):
        oirg_anim_index = int(self.frame_index)
        self.frame_index+=self.animation_speed
        new_anim_index = int(self.frame_index)
        if oirg_anim_index!=new_anim_index:
            if self.frame_index >= len(self.animations):
                self.frame_index-=len(self.animations)
                new_anim_index = int(self.frame_index)
            self.image = self.animations[new_anim_index]
            #self.rect = self.image.get_rect(center = self.hit_box.center)

class Bar(pygame.sprite.Sprite):
    def __init__(self, groups, character):
        super().__init__(groups)

        self.related_character = character
        self.bar_width = 100
        self.offset = pygame.math.Vector2(-25,-80)
        self.image = pygame.Surface([self.bar_width+2,12])
        self.update()
    
    def get_width(self):
        return max(self.bar_width*(self.related_character.health/self.related_character.max_health),0 )
    
    def update(self):
        self.image.fill((255,255,255))
        self.image.blit(pygame.Surface([self.get_width(),10]),(1,1))
        self.rect = self.image.get_rect(topleft = self.related_character.rect.center+self.offset)



class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface = pygame.Surface((const.TILESIZE,const.TILESIZE))):
        super().__init__(groups)
        #image = pygame.image.load('graphics/tile.png').convert_alpha()
        #self.image = pygame.transform.scale(image,(const.TILESIZE,const.TILESIZE))
        self.sprite_type = sprite_type
        self.image = surface
        if sprite_type == '2block':
            self.rect = self.image.get_rect(topleft=(pos[0],pos[1]-const.TILESIZE))
            self.hit_box = pygame.Rect(pos[0], pos[1], const.TILESIZE, const.TILESIZE).inflate(0,-10)

            #self.rect = self.image.get_rect(topleft = (pos[0],pos[1]-2*const.TILESIZE),width=const.TILESIZE, height=const.TILESIZE)
        else:
            self.rect = self.image.get_rect(topleft = pos)
            self.hit_box = self.rect.inflate(0,-10)


