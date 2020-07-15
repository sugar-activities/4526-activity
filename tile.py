#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Kuku Anakula
# Copyright (C) 2007, Julius B. Lucks, Adrian DelMaestro, Sera L. Young
# Copyright (C) 2012, Alan Aguiar
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact information:
# Julius B. Lucks <julius@younglucks.com>
# Alan Aguiar <alanjas@gmail.com>

# Includes class Tile which represents one tile on a grid.

import pygame
if not pygame.font: print ('Warning, fonts disabled')
from kuku_utils import load_image

class Tile(object):
    """One tile of the grid"""
    
    def __init__(self, x=0, y=0, tile_size_x = 0, tile_size_y = 0,offset=(0,0), scale_x=1.0):
        """make init on grid position as well"""
        # self.image = image
        # rect = image.get_rect()
        self.width = tile_size_x 
        self.height = tile_size_y       
        self.set_position(x,y,offset)
        self.answer = ''
        self.image_name = None 
        tam = int(70 * scale_x)
        self.fuente = pygame.font.Font(None, tam)
        self.font = None
        self.background = pygame.Surface(self.rect.size).convert()
        self.background.fill((255,255,255))    
    
    def __set_rect(self):
        """set the internal rectangle"""
        self.rect = pygame.Rect(self.x,self.y,self.width,self.height)

    
    def set_position(self,x,y,offset):
        """
        set the position of the tile in the grid
        
        x,y are non-negative integer grid positions
        """
        self.x = x*self.width  + offset[0]
        self.y = y*self.height + offset[1]
        self.__set_rect()
    
    def set_answer(self,answer=None,font=None,image_name=None):
        """set the answer"""
        self.answer = answer
        self.font = font
        self.image_name = image_name
        self.image = None
        if image_name:
            self.answer = image_name
            self.image_name = image_name
            self.image = load_image(self.image_name,1)
            scale_x = float(self.width )/float(self.image.get_rect().width)
            scale_y = float(self.height)/float(self.image.get_rect().height)
            self.image = pygame.transform.scale(self.image,
                                            (int(scale_x*self.image.get_rect().width),
                                             int(scale_y*self.image.get_rect().height)))
            self.background = self.image
        
        
    def get_answer(self):
        return self.answer
    
    def get_rect(self):
        """recturn the internal rectangle
        
        returns pygame.Rect() instance
        """
        return self.rect
    
    def draw(self,screen):
        """draw the tile in the rectangle
        
        returns list of pygame.Rect
        """
        # dirtyrects.append(screen.blit(self.image,self.rect))
        # return [screen.blit(self.image,self.rect)]
        dirtyrects = []
        
        #For some reason we have to do this, but seems like
        #a sloppy fix.  Need to maybe make png's and make
        #sure the transparency layer - see bug #1788        
        #This is needed when rendering font though
        r = screen.fill((255,255,255),self.rect)
        dirtyrects.append(r)
        
        #draw the answer
        if self.image_name:
            r = screen.blit(self.image, self.rect)  
            dirtyrects.append(r)
            
        elif self.font:
            br    = self.rect.bottomright
            
            text = self.fuente.render(str(self.answer), 1, (10, 10, 10))
            twidth = text.get_rect().width
            theight = text.get_rect().height
            textpos = (br[0]-twidth-10,br[1]-theight-5)
            dirtyrects.append(screen.blit(text, textpos))
        
        #draw the border
        dirtyrects.append(pygame.draw.rect(screen,(0,0,0),self.rect,1))
        return dirtyrects
    
    def get_background(self):
        """docstring for get_background"""
        return self.background
        
