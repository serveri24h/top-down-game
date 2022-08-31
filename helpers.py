from csv import reader
from os import walk
import pygame
import constants as const

def import_csv_layout(path):
    layout_list = []
    try:
        with open(path) as f:
            layout = reader(f,delimiter=',')
            for row in layout:
                layout_list.append([int(x) for x in row])
    except Exception as e:
        print("FAILED TO OPEN MAP",e)
    return(layout_list)

def import_folder(path,normalize=False):
    surface_list = []
    for _, __, file_list in walk(path):
        for f in file_list:
            full_path = path + '/' + f
            image = pygame.image.load(full_path).convert_alpha() 
            if normalize:
                image = pygame.transform.scale(image,(const.TILESIZE,const.TILESIZE))
            surface_list.append(image)
    return surface_list