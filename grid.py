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

import pygame
from tile import Tile

class Grid(object):
    """An grid that tiles images
    and manages positions.
    """
    def __init__(self, screen, dimensions, scale_x):
        grid_offset = (screen.width*(1./4.),0)
        
        self.dimensions = dimensions
        
        #hard-coded size of rect 900 x 900
        tile_size_x = (3./4.)*screen.width/self.dimensions[0]
        tile_size_y = screen.height/self.dimensions[1]
        
        #create tiles
        self.tiles = []
        #rects = []
        
        
        self.tiles = [Tile(x,y,tile_size_x,tile_size_y,grid_offset, scale_x) 
                         for x in range(self.dimensions[0]) 
                         for y in range(self.dimensions[1])]
                
        self.step_width = self.tiles[0].width
        self.step_height = self.tiles[0].height
        self.rect = pygame.Rect(0,0,0,0)
        self.rect = self.rect.unionall([t.get_rect() for t in self.tiles])
        self.center_position =(int(dimensions[0]/2),int(dimensions[1]/2))
    
    
    def get_tile(self,x,y):
        """get the tile at the grid position (x,y)
        raise an IndexError if not in grid.
        """
        if self.check_bounds(x,y):
            ind = self.dimensions[1]*x + y
            # print ("X,Y tulpa:[0,1] :",x,y,self.dimensions[0],self.dimensions[1])
            # print ('CAntidad de compo tiles',len(self.tiles)) 
            # print (self.tiles) 
            # print ("FIN")
            return self.tiles[int(ind)]
        else:
            raise IndexError
    
    
    def check_bounds(self,x,y):
        """make sure grid postion (x,y) fits within the grid"""
        if x > -1 and x < self.dimensions[0] and y > -1 and y < self.dimensions[1]:
           return True
        else:
           return False
    
    
    def draw(self,screen):
        """draws the tiles onto the screen"""
        dirtyrects = []
        for t in self.tiles:
            dirtyrects.extend(t.draw(screen))
        return dirtyrects
    
    def draw_tile(self,x,y,screen):
        ind = self.dimensions[1]*x + y
        t = self.tiles[int(ind)]
        dirtyrects = []
        dirtyrects.extend(t.draw(screen))
        return dirtyrects
    
    
    def update(self):
        """docstring for update"""
        pass
    
    def get_center_position(self):
        """docstring for get_center_position"""
        return self.center_position