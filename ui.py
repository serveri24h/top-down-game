import pygame
import constants

#UI_FONT = 'a'
UI_FONT_SIZE = 10
HEALTH_BAR_WIDTH = 200
BAR_HEIGHT = 20
UI_BG_COLOR = '#224422'
UI_BORDER_COLOR = '#444400'
HEALTH_COLOR = 'red'


class UI:
    def __init__(self):
        
        # General 
        self.display_surface = pygame.display.get_surface()
        #self.font = pygame.font.Font()

        # Bar setup
        self.health_bar_rect = pygame.Rect(10,10,HEALTH_BAR_WIDTH,BAR_HEIGHT)

    def show_bar(self,current,max_amount,bg_rect,rect_color):
        pygame.draw.rect(self.display_surface,UI_BG_COLOR,bg_rect)
        ratio = current/ max_amount
        current_width = bg_rect.width*ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        pygame.draw.rect(self.display_surface,rect_color,current_rect)
        pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,bg_rect,3)

    def display(self,player):
        self.show_bar(player.health,player.stats['HEALTH'],self.health_bar_rect,HEALTH_COLOR)