from distutils.log import debug
import pygame
import constants as const
import helpers as h
from tile import Weapon, Bar
from math import sin

HEALTH_BAR_WIDTH = 200
BAR_HEIGHT = 20
UI_BG_COLOR = '#224422'
UI_BORDER_COLOR = '#444400'
HEALTH_COLOR = 'red'


class Entity(pygame.sprite.Sprite):
    def __init__(self,groups):
        super().__init__(groups)
        self.frame_index = 0
        self.animation_speed = 0.17
        self.direction = pygame.math.Vector2()

        self.last_direction = 'down'
        self.status = 'idle'
        self.attack_time = 0
        self.damage_time = 0
        self.attack_cooldown = 300
        self.damage_cooldown = 500
        self.show_bar_cooldown = 3000
        self.can_take_damage  = True
        self.can_attack = True

    def move(self,speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        self.hit_box.x+=self.direction.x*speed
        self.collision('horizontal')
        self.hit_box.y+=self.direction.y*speed
        self.collision('vertical')
        self.rect.center=self.hit_box.center

    
    def collision(self,direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hit_box.colliderect(self.hit_box):
                    if self.direction.x > 0:
                        self.hit_box.right = sprite.hit_box.left
                    else:
                        self.hit_box.left = sprite.hit_box.right
        
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hit_box.colliderect(self.hit_box):
                    if self.direction.y > 0:
                        self.hit_box.bottom = sprite.hit_box.top
                    else:
                        self.hit_box.top = sprite.hit_box.bottom
    
    def flicker(self):
        if sin(pygame.time.get_ticks()) >= 0:
            alpha = 255
        else:
            alpha = 0
        self.image.set_alpha(alpha)

    def create_weapon(self):
        self.active_weapon = Weapon(self, [self.visible_sprites,self.attack_sprites])
    
    def destroy_weapon(self):
        if self.active_weapon:
            self.active_weapon.kill()
        self.active_weapon = None
    
    def hit_reaction(self):
        resistance = 150
        if self.can_take_damage == False:
            self.direction *= -resistance


class Enemy(Entity):
    def __init__(self, pos, groups, obstacle_sprites, attack_sprites):
        super().__init__(groups)

        # general setpu
        self.sprite_type = 'enemy'

        # graphics setup
        image = pygame.image.load('graphics/player_graphics/player_dummy.png').convert_alpha()
        self.image = pygame.transform.scale(image,(const.TILESIZE,const.TILESIZE))
        
        # movement
        self.rect = self.image.get_rect(topleft = pos)
        self.hit_box = self.rect.inflate(-30,-20)
        self.obstacle_sprites = obstacle_sprites
        self.visible_sprites = groups[0]
        self.attack_sprites = attack_sprites


        self.health_bar = None
        
        # graphics
        self.import_graphics()

        # stats
        self.speed = const.CHARACTER_SPEED/2
        self.health = 50
        self.max_health = 50
        self.attack_anim_cooldown = 400
        self.attack_cooldown = 2000
        self.attack_time = None
        self.attack_radius = 100
        self.move_radius = 400

        # player interaction

    
    def import_graphics(self):
        graphics_path = 'graphics/enemy_graphics/'
        self.animations = { 'up_move':[],'down_move':[],'right_move':[],'left_move':[],
                            'up_idle':[],'down_idle':[],'right_idle':[],'left_idle':[],
                            'up_attack':[],'down_attack':[],'right_attack':[],'left_attack':[]
        }
        for animation in self.animations.keys():
            self.animations[animation] = h.import_folder(graphics_path+animation, normalize=True)
    
    def animate(self):
        anim_key = self.last_direction+'_'+self.status
        oirg_anim_index = int(self.frame_index)
        self.frame_index+=self.animation_speed
        new_anim_index = int(self.frame_index)
        if oirg_anim_index!=new_anim_index:
            animation = self.animations[anim_key]
            if self.frame_index >= len(animation):
                self.frame_index -= len(animation)
            self.image = animation[int(self.frame_index)]
            self.rect = self.image.get_rect(center = self.hit_box.center)
        
        if self.can_take_damage == False:
            self.flicker()
    
    def get_player_distance_direction(self,player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec-enemy_vec).magnitude()
        if distance > 0:
            direction = (player_vec-enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()
        return distance,direction

    def get_status(self, player):
        self.distance,self.direction = self.get_player_distance_direction(player)
        if self.direction[0]**2>self.direction[1]**2:
            if self.direction[0]>0:
                self.last_direction = 'right'
            else:
                self.last_direction = 'left'
        else:
            if self.direction[1]>0:
                self.last_direction = 'down'
            else:
                self.last_direction = 'up'

        if self.status != 'attack':
            if self.distance <= self.attack_radius and self.can_attack:
                self.status = 'attack'
                self.attack_time = pygame.time.get_ticks()
                self.create_weapon()
                self.can_attack = False
            elif self.distance < self.move_radius:
                self.status = 'move'
            else:
                self.direction = pygame.math.Vector2()
                self.status = 'idle'
        else:
            self.direction.x = 0
            self.direction.y = 0

    def create_health_bar(self,groups):
        self.health_bar = Bar(groups,self)
    
    def destroy_enemy(self):
        if self.health_bar:
            self.health_bar.kill()
        if self.active_weapon:
            self.active_weapon.kill()
        self.kill()

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.status == 'attack' and current_time - self.attack_time >= self.attack_anim_cooldown:
            self.status = 'idle'
            self.destroy_weapon()
        elif self.can_attack == False and current_time - self.attack_time >= self.attack_cooldown:
            self.can_attack = True
        
        if self.can_take_damage == False:
            self.hit_reaction()
            if current_time - self.damage_time >= self.damage_cooldown:
                self.can_take_damage = True
                self.image.set_alpha(255)
           
        if self.health_bar and current_time - self.damage_time >= self.show_bar_cooldown:
            self.health_bar.kill()
            self.health_bar = None

    def get_damage(self,attack,groups,attack_sprite_type):
        if self.can_take_damage:
            if attack_sprite_type == 'weapon':
                self.direction = attack.direction
                self.health -= attack.damage
                self.can_take_damage = False
                if not self.health_bar:
                    self.create_health_bar(groups)
                self.damage_time = pygame.time.get_ticks()

    def update(self):
        self.cooldowns()
        self.animate()
        self.move(self.speed)



class Player(Entity):
    def __init__(self, pos, groups,obstacle_sprites,attack_sprites):
        super().__init__(groups)
        image = pygame.image.load('graphics/player_graphics/player_dummy.png').convert_alpha()
        self.image = pygame.transform.scale(image,(const.TILESIZE,const.TILESIZE))
        self.rect = self.image.get_rect(topleft = pos)
        self.hit_box = self.rect.inflate(-30,-20)

        self.import_graphics()

        # Status
        self.last_direction = 'down'
        self.status = 'idle'
        self.attack_cooldown = 400
        self.attack_time = None

        self.visible_sprites = groups[0]
        self.obstacle_sprites = obstacle_sprites
        self.attack_sprites = attack_sprites

        # Attack Sprites
        self.active_weapon = None

        # Stats
        self.stats = {'HEALTH':100}
        self.health = self.stats['HEALTH']
        self.speed = const.CHARACTER_SPEED

        # Player Signal
        self.change_level = False

    
    def import_graphics(self):
        graphics_path = 'graphics/player_graphics/'
        self.animations = { 'up_move':[],'down_move':[],'right_move':[],'left_move':[],
                            'up_idle':[],'down_idle':[],'right_idle':[],'left_idle':[],
                            'up_attack':[],'down_attack':[],'right_attack':[],'left_attack':[]
        }

        for animation in self.animations.keys():
            #print(animation)
            self.animations[animation] = h.import_folder(graphics_path+animation, normalize=True)
    
    def input(self):
        keys_pressed = pygame.key.get_pressed()

        # INPUT CHECK
        if self.status != 'attack':
            # MOVEMENT INPUT
            if keys_pressed[pygame.K_UP]:
                self.direction.y = -1
                self.last_direction = 'up'
                self.status = 'move'
            elif keys_pressed[pygame.K_DOWN]:
                self.direction.y = 1
                self.last_direction = 'down'
                self.status = 'move'
            else:
                self.direction.y = 0
                self.status = 'idle'

            if keys_pressed[pygame.K_LEFT]:
                self.direction.x = -1
                self.last_direction = 'left'
                self.status = 'move'
            elif keys_pressed[pygame.K_RIGHT]:
                self.direction.x = 1
                self.last_direction = 'right'
                self.status = 'move'
            else:
                self.direction.x = 0
            
            # ATTACK INPUT

            if keys_pressed[pygame.K_SPACE]:
                self.status = 'attack'
                self.direction.x = 0
                self.direction.y = 0
                self.attack_time=pygame.time.get_ticks()
                self.create_weapon()
            
            # MAGIC

            if keys_pressed[pygame.K_x]:
                self.attack_time=pygame.time.get_ticks()
                self.status = 'attack'
                self.direction.x = 0
                self.direction.y = 0

        if keys_pressed[pygame.K_1]:
            self.change_level = True
            self.new_level = 1

        if keys_pressed[pygame.K_2]:
            self.change_level = True
            self.new_level = 2

    
    def animate(self):
        anim_key = self.last_direction+'_'+self.status
        oirg_anim_index = int(self.frame_index)
        self.frame_index+=self.animation_speed
        new_anim_index = int(self.frame_index)
        if oirg_anim_index!=new_anim_index:
            animation = self.animations[anim_key]
            if self.frame_index >= len(animation):
                self.frame_index -= len(animation)
            self.image = animation[int(self.frame_index)]
            self.rect = self.image.get_rect(center = self.hit_box.center)
        
        if self.active_weapon:
            self.active_weapon.animate()

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.status == 'attack':
            if current_time - self.attack_time >= self.attack_cooldown:
                self.status = 'idle'
                self.destroy_weapon()
        
        if self.can_take_damage == False:
            self.hit_reaction()
            if current_time - self.damage_time >= self.damage_cooldown:
                self.can_take_damage = True
                self.image.set_alpha(255)
    
    def get_damage(self,attack):
        if self.can_take_damage:
            if attack.sprite_type == 'weapon':
                self.direction = attack.direction
                self.can_take_damage = False
                self.health -= attack.damage
                self.damage_time = pygame.time.get_ticks()

    def update(self):
        input_int = self.input()
        self.cooldowns()
        self.animate()
        self.move(self.speed)
        return input_int
    
    def die(self):
        if self.active_weapon:
            self.active_weapon.kill()
        self.kill()

    def get_player_signal(self):
        if self.change_level == True:
            return self.new_level
        else:
            return -1