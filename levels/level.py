import pygame
import constants as const
import helpers as h
from tile import Tile, Weapon
from player import Player,Enemy
from ui import UI

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self,bg_image,scale_background=False):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0]//2
        self.half_height = self.display_surface.get_size()[1]//2
        self.offset = pygame.math.Vector2()
        self.floor_surface = pygame.image.load(bg_image).convert()
        if scale_background:
            self.floor_surface = pygame.transform.scale(self.floor_surface,(10*const.TILESIZE,10*const.TILESIZE))
        self.floor_rect = self.floor_surface.get_rect(topleft = (0,0))
    
    def custom_draw(self,player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surface,floor_offset_pos)

        for sprite in sorted(self.sprites(),key=lambda sprite: sprite.rect.centery):
            offset_position = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image,offset_position)

    def enemy_update(self,player):
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.get_status(player)
        

class Level():
    def __init__(self, map_layout_path,player_pos,scale_background=False):
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite group setup
        self.visible_sprites = YSortCameraGroup(map_layout_path+'background.png',scale_background=scale_background)
        self.obstacles_sprites = pygame.sprite.Group()
        self.transport_sprites = pygame.sprite.Group()

        self.hero_attack_sprites = pygame.sprite.Group()
        self.enemy_attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        self.create_map(map_layout_path,player_pos)
        self.ui = UI()
    
    def create_map(self,map_layout_path,player_pos):
    
        layouts = {
            'boundary': h.import_csv_layout(map_layout_path+'map_layout_boundaries.csv'),
            'object': h.import_csv_layout(map_layout_path+'map_layout_objects.csv'),
            'house': h.import_csv_layout(map_layout_path+'map_layout_houses.csv'),
            'entities': h.import_csv_layout(map_layout_path+'map_layout_entities.csv'),
            'teleports': h.import_csv_layout(map_layout_path+'map_layout_teleports.csv')
        }

        object_images = {
            0: None,
            4: ['2block',pygame.image.load('graphics/tree.png').convert_alpha()],
            5: ['1block',pygame.image.load('graphics/bush.png').convert_alpha()],
            6: ['1block',pygame.image.load('graphics/rock.png').convert_alpha()]
        }

        house_image = pygame.image.load('graphics/house_template.png').convert_alpha()
        house_parts = {}
        for i in range(4):
            for j in range(4):
                house_parts[i*4+j] = house_image.subsurface((j*const.TILESIZE,i*const.TILESIZE,const.TILESIZE,const.TILESIZE))


        for style,layout in layouts.items():
            for row_index,row in enumerate(layout):
                for col_index,element in enumerate(row):
                    if element > -1:
                        x = col_index * const.TILESIZE
                        y = row_index * const.TILESIZE
                        if style == 'boundary':
                            Tile((x,y),[self.obstacles_sprites],'invisible')
                        if style == 'object' and element>0:
                            Tile((x,y),[self.obstacles_sprites,self.visible_sprites],object_images[element][0],object_images[element][1])
                        if style == 'house':
                            Tile((x,y),[self.obstacles_sprites,self.visible_sprites],'1block',house_parts[element])
                        if style == 'entities':
                            Enemy((x,y),[self.visible_sprites,self.attackable_sprites],self.obstacles_sprites,self.enemy_attack_sprites)
                        if style == 'teleports':
                            Tile((x,y),[self.transport_sprites],'teleport')


        self.player = Player(player_pos,[self.visible_sprites],self.obstacles_sprites,self.hero_attack_sprites)
    
    def player_attack_logic(self):
        if self.hero_attack_sprites:
            for attack_sprite in self.hero_attack_sprites:
                hero_collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
                if hero_collision_sprites:
                    for target_sprite in hero_collision_sprites:
                        if target_sprite.sprite_type == 'enemy':
                            target_sprite.get_damage(self.player.active_weapon,[self.visible_sprites],attack_sprite.sprite_type)
                            if target_sprite.health <= 0:
                                target_sprite.destroy_enemy()
                        else:
                            pass
        if self.enemy_attack_sprites:
            enemy_collision_sprites = pygame.sprite.spritecollide(self.player,self.enemy_attack_sprites,False)
            if enemy_collision_sprites:
                self.player.get_damage(enemy_collision_sprites[0])
                if self.player.health < 0:
                    self.player.die()
        if self.transport_sprites:
            transport_collision_sprites = pygame.sprite.spritecollide(self.player,self.transport_sprites,False)
            if transport_collision_sprites:
                self.player.change_level = True
                self.player.new_level = 2



    
    def run(self):
        # update and draw the level/game
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.enemy_update(self.player)
        self.ui.display(self.player)
        self.player_attack_logic()
        self.visible_sprites.update()
        return self.player.get_player_signal()
