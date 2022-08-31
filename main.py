import pygame
import sys

import constants as const
from levels.level import Level
        

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
        pygame.display.set_caption("Serveri24h Top-Down Game Template")
        self.clock = pygame.time.Clock()


        # Main level
        main_level_path = 'maps/test_map/'
        side_level_path = 'maps/side_map/'
        self.main_level = Level(main_level_path,(1410,2993))
        self.side_level = Level(side_level_path,(150,150),scale_background=True)
        self.current_level = self.main_level
    
    def run_level(self,level):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill((0,50,255))
        player_signal = level.run()
        pygame.display.update()
        return player_signal


    def run(self):
        while True:
            player_signal = self.run_level(self.current_level)
            if player_signal == 1:
                self.current_level = self.main_level
            elif player_signal == 2:
                self.current_level = self.side_level
            self.clock.tick(const.FPS)
            

if __name__=='__main__':
    game = Game()
    game.run()
