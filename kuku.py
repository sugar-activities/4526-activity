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

import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import pygame
import random
from pygame.locals import Rect
from grid import Grid
import question
import re

from kuku_utils import data_path, load_image
from kuku_config import GRID_SIZE, GAME_TIME
from kuku_config import PLAYER_LIVES, QUESTION_FILES

from gettext import gettext as _

scale_x = 1.0
scale_y = 1.0


dirtyrects = [] # list of update_rects


# container for images
class Images():

    def __init__(self, scale_x, scale_y):

        # Load player images
        kuku = load_image('kuku_default.png',1)
        kuku_peck = load_image('kuku_pecking.png',1)
        kuku_stunned = load_image('kuku_stunned.png',1)
        kuku_happy = load_image('kuku_happy.png',1)
        kuku_game_start = load_image('kuku_startpage.png',1)
        kuku_game_over = load_image('kuku_endpage.png',1)
        kuku_game_win = load_image('kuku_win.png',1)
        kuku_num_correct = load_image('kuku_num_correct.png',1)
        kuku_high_score = load_image('kuku_high_score.png',1)
        kuku_clock = load_image('kuku_clock.png',1)

        self.game_start = pygame.transform.scale(kuku_game_start,
                                                (int(scale_x*kuku_game_start.get_rect().width),
                                                 int(scale_y*kuku_game_start.get_rect().height)))

        self.game_over = pygame.transform.scale(kuku_game_over,
                                                (int(scale_x*kuku_game_over.get_rect().width),
                                                 int(scale_y*kuku_game_over.get_rect().height)))

        self.game_win = pygame.transform.scale(kuku_game_win,
                                                (int(scale_x*kuku_game_win.get_rect().width),
                                                 int(scale_y*kuku_game_win.get_rect().height)))

        self.player_right = pygame.transform.scale(kuku,
                                                  (int(scale_x*kuku.get_rect().width),
                                                  int(scale_y*kuku.get_rect().height)))
        self.player_left = pygame.transform.flip(self.player_right,1,0)
        self.peck_right = pygame.transform.scale(kuku_peck,
                                (int(scale_x*kuku_peck.get_rect().width),
                                int(scale_y*kuku_peck.get_rect().height)))
        self.peck_left = pygame.transform.flip(self.peck_right,1,0)

        #change this to get image correct
        self.lives = pygame.transform.scale(kuku_peck,
                                (int(scale_x*kuku_peck.get_rect().width),
                                int(scale_y*kuku_peck.get_rect().height)))

        self.correct = pygame.transform.scale(kuku_num_correct,
                                (int(scale_x*kuku_num_correct.get_rect().width),
                                 int(scale_y*kuku_num_correct.get_rect().height)))

        self.high_score = pygame.transform.scale(kuku_high_score,
                                (int(scale_x*kuku_high_score.get_rect().width),
                                 int(scale_y*kuku_high_score.get_rect().height)))

        #clock
        self.timer =   pygame.transform.scale(kuku_clock,
                                (int(scale_x*kuku_clock.get_rect().width),
                                 int(scale_y*kuku_clock.get_rect().height)))

        self.stunned_right = pygame.transform.scale(kuku_stunned,
                                                (int(scale_x*kuku_stunned.get_rect().width),
                                                 int(scale_y*kuku_stunned.get_rect().height)))
        self.stunned_left = pygame.transform.flip(self.stunned_right,1,0)

        self.happy_right = pygame.transform.scale(kuku_happy,
                                                   (int(scale_x*kuku_happy.get_rect().width),
                                                    int(scale_y*kuku_happy.get_rect().height)))
        self.happy_left = pygame.transform.flip(self.happy_right,1,0)


class State(object):
    """State object

    maintaines score, lives, high
    score, etc.
    """

    def __init__(self):
        self.score = 0
        self.lives = PLAYER_LIVES
        self.high_score = 0
        self.time = GAME_TIME
        self.won = 0

    def __str__(self):
        str = 'score %i\n lives %i\n High Score %i\n Time %i\n Won %i \n' %\
              (self.score,self.lives,self.high_score,self.time,self.won)
        return str

    def save(self):
        """save state object in kuku_state.obj"""
        try:
            f = file(data_path('kuku_state.obj'), "w")
            f.write(str(self.score) + "\n")
            f.write(str(self.lives) + "\n")
            f.write(str(self.high_score) + "\n")
            f.write(str(self.time) + "\n")
            f.close()
        except Exception as err:
            print (' Save Error saving scores', err)

    def update(self,lives=None,score=None,time=None):
        """update lives, score and time"""

        #update score and time
        self.score = score or self.score
        self.time  = time  or self.time

        #if you have not lost a life (i.e. have a correct answer),
        # your score is greater than 0, and a multiple of 10,
        # then you have won
        # (you have not one if your score is >0 and a multiple of 10,
        #   and you have just lost a life)
        if lives == self.lives and self.score > 0 and self.score%10 ==0:
            self.won = 1

        #update lives
        self.lives = lives or self.lives

        if self.high_score < self.score:
            self.high_score = self.score

        # if self.score > 0 and self.score%10 ==0:
        #     self.won = 1

        # print self


class Actor:
    "An enhanced sort of sprite class"
    def __init__(self, image):
        self.set_image(image)
        self.rect = image.get_rect()

    def update(self):
        "update the sprite state for this frame"
        pass

    def set_image(self,image):
        """set a new image"""
        self.image = image

    def draw(self, screen):
        "draws the sprite into the screen"
        r = screen.blit(self.image, self.rect)
        return r

    def erase(self, screen, background):
        "gets the sprite off of the screen"
        r = screen.blit(background, self.rect, self.rect)
        return r

    def get_rect(self):
        return self.rect

class Player(Actor):
    "Cheer for our hero"
    def __init__(self,grid, img):
        """grid is the grid the player lives on"""
        Actor.__init__(self, img.player_right)
        self.alive = 1
        self.grid = grid
        self.grid_position = self.grid.get_center_position()
        self.set_rect_position(self.image)
        self.img_player_left = img.player_left
        self.img_player_right = img.player_right

    def set_rect_position(self,cimage):
        """set_rect_position based on grid_position"""
        #get tile based on grid position
        #if can't find tile, then don't move
        try:
            t = self.grid.get_tile(self.grid_position[0],
                                   self.grid_position[1])
            self.rect.centerx = t.rect.centerx

            if (cimage.get_rect().height == int(130*scale_y)):
                self.rect.centery = t.rect.centery
            else:
                self.rect.centery = t.rect.centery - int(24*scale_y)


        except IndexError:
            pass

    def move(self, x_direction,y_direction):

        #step = +/- 1
        x_step = 0
        y_step = 0
        if x_direction:
            x_step = x_direction/abs(x_direction)
        if y_direction:
            y_step = y_direction/abs(y_direction)

        #change image to reflect right and left
        if x_step < 0:
            self.set_image(self.img_player_left)
        elif x_direction > 0:
            self.set_image(self.img_player_right)
            #step = 1
        #elif y_direction != 0:
            #self.set_image(Img.player_right)

        self.move_grid_position(x_step,y_step)
        self.set_rect_position(self.image)


    def move_grid_position(self,x_step,y_step):
        """docstring for move_grid_position"""
        #check grid bounds
        new_position = [self.grid_position[0] + x_step,
                        self.grid_position[1] + y_step]
        # print 'N',new_position
        if self.grid.check_bounds(new_position[0],new_position[1]):
            self.grid_position = new_position


class QuestionAnswer:
    """The question/answer class.

    Displays the questions as well as answers on the screen"""

    def __init__(self, gridsize,q,answer_pool=None):
        self.Nx = gridsize[0]
        self.Ny = gridsize[1]
        self.question = q
        self.question_string = self.question.q_string
        self.answer_pool = answer_pool

        self.answers = []

        if self.question.type == question.N_TYPE:

            self.correct_answer = self.question.a_list[0]
            while (len(self.answers) < self.Nx*self.Ny):
                ind = random.randint(0,len(answer_pool)-1)
                self.answers.append(answer_pool[ind])
            if not (self.correct_answer in self.answers):
                correct_index = random.randint(0,self.Nx*self.Ny-1)
                self.answers[correct_index] = self.correct_answer

        elif self.question.type == question.MULTIPLES_TYPE:

            #draw random possibility
            ind = random.randint(0,self.question.n_answers-1)
            self.correct_answer = int(self.question.a_list[ind])

            #dirty hack to get which number multiples of
            self.q_num = int(re.findall('\d',self.question.q_string_raw)[0])
            if self.correct_answer < 10:
                maxans = 50
            else:
                maxans = 3*self.correct_answer

            while (len(self.answers) < self.Nx*self.Ny):
                # Construct a random integer between 0 and maxans
                rand_ans = random.randint(0,maxans)
                # test if we have that answer yet, if not add to list
                # make sure no multiples
                if (rand_ans%self.q_num != 0) and \
                    not (rand_ans in self.answers):
                    self.answers.append(rand_ans)

            # now put the correct answer in a random location if
            # it doesn't already exist by accident
            if not (self.correct_answer in self.answers):
                correct_index = random.randint(0,self.Nx*self.Ny-1)
                self.answers[correct_index] = self.correct_answer

        else:
            self.correct_answer = int(self.question.a_list[0])
            # print self.correct_answer

            if self.correct_answer < 10:
                maxans = 50
            else:
                maxans = 3*self.correct_answer

            while (len(self.answers) < self.Nx*self.Ny):
                # Construct a random integer between 0 and maxans
                rand_ans = random.randint(0,maxans)
                # test if we have that answer yet, if not add to list
                if not (rand_ans in self.answers):
                    self.answers.append(rand_ans)

            # now put the correct answer in a random location if
            # it doesn't already exist by accident
            if not (self.correct_answer in self.answers):
                correct_index = random.randint(0,self.Nx*self.Ny-1)
                self.answers[correct_index] = self.correct_answer


    def get_correct_answer(self):
        return self.correct_answer

    def display_question(self,screen,font):
        """Display the question on the screen."""
        tam = 80 * scale_x
        font = pygame.font.Font(None, int(tam))
        text = font.render(self.question_string + ' ?',1,(255,10,10))

        # print self.question_string

        #if text to wide, decrease font_size until
        #it fits
        #font_size = FONT_SIZE
        #while text.get_rect().width > 300.*scale_x:
        #    font_size = int(font_size*2./3.)
            #font = pygame.font.Font(None, font_size)
            #text = font.render(self.question_string,1,(10,10,10))
        #font = pygame.font.Font(None, 60)

        tlcorner = screen.get_rect().topleft
        textpos = (tlcorner[0] + 5, tlcorner[1] + 10)
        
        return [screen.blit(text,textpos)]

    def set_answers(self,screen,grid,font):
        '''Displays question answers in the BRH corner of each game tile.'''

        for x in range(self.Nx):
            for y in range(self.Ny):
                tilenum = x + y*self.Ny
                if self.question.type != question.N_TYPE:
                    grid.get_tile(x,y).set_answer(answer=self.answers[tilenum],
                                                  font=font)
                elif self.question.type == question.N_TYPE:
                    grid.get_tile(x,y).set_answer(image_name=self.answers[tilenum])


class Time(object):

    def __init__(self,number,image,screen,font):
        self.number = number
        self.font = font
        self.update = 1
        self.image = image
        screen_rect = screen.get_rect()
        image_rect = self.image.get_rect()

        #max width is 3 digits
        self.text = self.font.render(str(100),1,(10,10,10))

        self.rect = pygame.Rect(screen_rect.left,
                                (4./8.)*screen_rect.bottom-image_rect.height,
                                image_rect.width+self.text.get_rect().width,
                                image_rect.height)
    def draw(self,screen):
        """draw the number of lives left"""
        dirtyrects = []
        # print 'score'
        if self.update:
            #white out
            r = screen.fill((255,255,255),self.rect)
            dirtyrects.append(r)

            r = screen.blit(self.image, self.rect)
            dirtyrects.append(r)

            self.text = self.font.render(str(self.number),1,(10,10,10))
            textpos = (self.rect.right - self.text.get_rect().width,
                       self.rect.bottom - self.text.get_rect().height
                      )

            dirtyrects.append(screen.blit(self.text,textpos))

        self.update = 0
        return dirtyrects

    def add(self,number):
        """docstring for add"""
        self.number += number
        self.update = 1

    def set(self,number):
        """docstring for set"""
        self.number = number

    def get_ticks(self):
        return self.number


class Score(object):
    """keeps Score"""
    def __init__(self,number,image,screen,font):
        self.number = number
        self.font = font
        self.update = 1
        self.image = image
        screen_rect = screen.get_rect()
        image_rect = self.image.get_rect()

        #max width is 3 digits
        self.text = self.font.render(str(100),1,(10,10,10))

        self.rect = pygame.Rect(screen_rect.left,
                                (3./4.)*screen_rect.bottom-image_rect.height,
                                image_rect.width+self.text.get_rect().width,
                                image_rect.height)


    def draw(self,screen):
        """draw the number of lives left"""
        dirtyrects = []
        # print 'score'
        if self.update:
            #white out
            screen.fill((255,255,255),self.rect)

            r = screen.blit(self.image, self.rect)
            dirtyrects.append(r)

            self.text = self.font.render(str(self.number),1,(10,10,10))
            textpos = (self.rect.right - self.text.get_rect().width,
                       self.rect.bottom - self.text.get_rect().height
                      )

            dirtyrects.append(screen.blit(self.text,textpos))

        self.update = 0
        return dirtyrects

    def add(self,number):
        """docstring for add"""
        self.number += number
        self.update = 1

    def set(self,number):
        """docstring for set"""
        self.number = number
        self.update = 1

    def get_score(self):
        """docstring for get_score"""
        return self.number


class HighScore(Score):
    """HighScore"""
    def __init__(self,number,image,screen,font):
        Score.__init__(self,number,image,screen,font)
        screen_rect = screen.get_rect()
        image_rect = self.image.get_rect()
        self.rect = pygame.Rect(screen_rect.left,
                                (5./8.)*screen_rect.bottom-image_rect.height,
                                image_rect.width+self.text.get_rect().width,
                                image_rect.height)



class Lives(object):

    def __init__(self,number,image,screen,font):
        self.number = number
        self.font = font
        self.update = 1
        self.image = image
        # self.text_width = 10
        self.vertical_offset = 10
        screen_rect = screen.get_rect()
        image_rect = self.image.get_rect()

        self.text = self.font.render(str(self.number),1,(10,10,10))

        self.rect = pygame.Rect(screen_rect.left,
                                screen_rect.bottom-self.vertical_offset-image_rect.height,
                                image_rect.width+self.text.get_rect().width,
                                image_rect.height)

    def draw_lives(self,screen):
        """draw the number of lives left"""
        dirtyrects = []

        if self.update:
            #white out
            screen.fill((255,255,255),self.rect)

            r = screen.blit(self.image, self.rect)
            dirtyrects.append(r)

            self.text = self.font.render(str(self.number),1,(10,10,10))
            textpos = (self.rect.right - self.text.get_rect().width,
                       self.rect.bottom - self.text.get_rect().height
                      )

            dirtyrects.append(screen.blit(self.text,textpos))

        self.update = 0
        return dirtyrects

    def kill(self):
        """take one life (never drop below zero)"""
        self.number -= 1
        self.update = 1

    def get_lives(self):
        """docstring for get_lives"""
        return self.number

    def set_lives(self,number):
        """docstring for set_lives"""
        self.number = number
        self.update = 1


class KukuActivity():

    def __init__(self, running_sugar=True):

        self.running_sugar = running_sugar
        #Initialize questions - need to do lazy loading to speed up game init
        self.question_lists = []
        qfIO = question.QuestionFileIO()
        for question_file in QUESTION_FILES:
            try:
                #print question_file
                question_list = qfIO.Read_questions(data_path(question_file))
            except question.ParseError:
                print ('Problem parsing file, using random questions.')
                qs = []
                for j in range(100):
                    q = (random.randint(0,9),
                         random.randint(0,9))
                    question_string = '%i x %i = ?' % q
                    answer = '%i' % (q[0]*q[1])
                    qs.append(question.Question(question_string,
                                                             answer))
                    question_list = question.QuestionList(qs)
            self.question_lists.append(question_list)
        self.question_group = question.QuestionGroup(self.question_lists)

    def game_over(self, screen, gridsize, font):
        """the game over screen"""
        screen.fill((255,255,255))
        vec = (screen.get_rect().center[0]-self.Img.game_over.get_rect().center[0],
               screen.get_rect().center[1]-self.Img.game_over.get_rect().center[1],
        )
        r = self.Img.game_over.get_rect()
        r = r.move(vec[0],vec[1])
        screen.blit(self.Img.game_over,r)
        pygame.display.update()
        while True:
            # Pump GTK messages.
            while Gtk.events_pending():
                Gtk.main_iteration()
            events = pygame.event.get()
            for evt in events:
                if evt.type == pygame.QUIT:
                    sys.exit(0)
                elif evt.type == pygame.KEYDOWN:
                    qa,num_players,score,time_clock = self.game_start(screen,gridsize,font)
                    return (qa,num_players,score,time_clock)

    def game_win(self, screen, gridsize, font):
        """the game over screen"""
        screen.fill((255,255,255))
        vec = (screen.get_rect().center[0]-self.Img.game_win.get_rect().center[0],
               screen.get_rect().center[1]-self.Img.game_win.get_rect().center[1],
        )
        r = self.Img.game_win.get_rect()
        r = r.move(vec[0],vec[1])
        screen.blit(self.Img.game_win,r)
        pygame.display.update()
        # print 'win!!', state
        while True:
            # Pump GTK messages.
            while Gtk.events_pending():
                Gtk.main_iteration()
            events = pygame.event.get()
            for evt in events:
                if evt.type == pygame.QUIT:
                    sys.exit(0)
                elif evt.type == pygame.KEYDOWN:
                    qa,num_players,score,time_clock = self.game_start(screen,gridsize,font,started=1)
                    score.set(self.state.score)
                    return (qa,num_players,score,time_clock)


    def game_start(self, screen, gridsize, font, started=1):
        """the game over screen"""
        # Start music
        pygame.mixer.music.load(data_path('kuku_slow.ogg'))
        pygame.mixer.music.play(-1,0.0)

        if not started:
            screen.fill((255,255,255))
            vec = (screen.get_rect().center[0]-self.Img.game_start.get_rect().center[0],
                   screen.get_rect().center[1]-self.Img.game_start.get_rect().center[1],
            )
            r = self.Img.game_start.get_rect()
            r = r.move(vec[0],vec[1])
            screen.blit(self.Img.game_start,r)

            message = _('Begin!')
            text = font.render(message,1,(10,10,10))
            twidth = text.get_rect().width
            #theight = text.get_rect().height
            tlcorner = screen.get_rect().center
            textpos = (tlcorner[0]-twidth/2, tlcorner[1])

            screen.blit(text,textpos)
            pygame.display.flip()

            while True:
                # Pump GTK messages.
                while Gtk.events_pending():
                    Gtk.main_iteration()
                events = pygame.event.get()
                for evt in events:
                    if evt.type == pygame.QUIT:
                        sys.exit(0)
                    elif evt.type == pygame.KEYDOWN:
                        qa,num_players,score,time_clock = self.reset_board(screen,gridsize,font)
                        return (qa,num_players,score,time_clock)
        else:
            started = 1
            qa,num_players,score,time_clock = self.reset_board(screen,gridsize,font)
            return (qa,num_players,score,time_clock)



    def reset_board(self, screen, gridsize, font,
                    num_players=None, score=None,
                    time_clock=None):
        """docstring for reset_board"""
        # Stop all sounds
        #pygame.mixer.stop()

        # # Start music
        # pygame.mixer.music.load(data_path('kuku_slow.ogg'))
        # pygame.mixer.music.play(-1,0.0)

        question_list = self.question_group.next()
        q = question_list.next()
        # print q.a_string, q.a_type
        qa = QuestionAnswer(gridsize,q,
                            answer_pool=question_list.get_all_answers())

        if not num_players:
            num_players = Lives(PLAYER_LIVES,self.Img.lives,screen,font)
        else:
            num_players.update = 1

        if not score:
            score = Score(0,self.Img.correct,screen,font)
        else:
            score.update = 1

        if not time_clock:
            time_clock = Time(GAME_TIME,self.Img.timer,screen,font)

        screen.fill((255,255,255))
        pygame.display.update()
        return (qa,num_players,score,time_clock)

    def save_state(self, PLAYER_LIVES, GAME_TIME):
        print ('Saving state...')
        #self.state.score = 0
        self.state.lives = PLAYER_LIVES
        self.state.time  = GAME_TIME
        self.state.save()
        print ('State saved')


    def load_state(self):
        self.state = State()
        try:
            f = open(data_path('kuku_state.obj'),'r')
            self.state.score = int(f.readline())
            self.state.lives = int(f.readline())
            self.state.high_score = int(f.readline())
            self.state.time = int(f.readline())
            f.close()
        except Exception as err:
            print ('LOADCannot open kuku_state.obj', err)


    def run(self):
        """main pygame loop"""

        global dirtyrects
        global scale_x, scale_y
        move_keys = [pygame.K_UP,
                     pygame.K_DOWN,
                     pygame.K_LEFT,
                     pygame.K_RIGHT,
                     pygame.K_KP8,
                     pygame.K_KP6,
                     pygame.K_KP2,
                     pygame.K_KP4,
                     pygame.K_ESCAPE
        ]

        pygame.init()
        pygame.display.init()
        #screen = pygame.display.set_mode(SCREENRECT.size,0)
        screen = pygame.display.get_surface()

        if not(screen):
            info = pygame.display.Info()
            w = info.current_w
            h = info.current_h
            # prevent hide zones
            #w = w - 50
            #h = h - 100
            screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)

        #whiten screen
        screen.fill((255,255,255))

        w = screen.get_width()
        h = screen.get_height()
        if (w == 1200) and (h > 825):
            SCREENRECT = Rect(0,0,1200,825)
            scale_x = 1.0
            scale_y = 1.0
            FONT_SIZE = 36
        else:
            h = h - 20
            FONT_SIZE = 36
            ancho = w
            altura = h
            if (w/1200.0) < (h/825.0):
                scale_x = w/1200.0
                scale_y = scale_x
                altura = (825.0*scale_x)
            else:
                scale_y = h/825.0
                scale_x = scale_y
                ancho = (1200.0*scale_y)
            SCREENRECT = Rect(0,0,int(ancho),int(altura))

        # make background
        background = pygame.Surface(SCREENRECT.size).convert()
        background.fill((255,255,255))
        screen.blit(background, (0,0))
        pygame.display.flip()
           

        self.load_state()

        # # Start music
        # pygame.mixer.music.load(data_path('kuku_slow.ogg'))
        # pygame.mixer.music.play(-1,0.0)

        # load game sounds
        bock = pygame.mixer.Sound(data_path('bock.ogg'))
        peck_good = pygame.mixer.Sound(data_path('peckgood.ogg'))
        peck_bad = pygame.mixer.Sound(data_path('peckbad.ogg'))
        kuku_lose = pygame.mixer.Sound(data_path('kuku_death.ogg'))
        kuku_win = pygame.mixer.Sound(data_path('kuku_win.ogg'))

        # load images
        self.Img = Images(scale_x, scale_y)

        # create a font instance
        font = pygame.font.Font(None, FONT_SIZE)

        # set the gridsize
        gridsize = (GRID_SIZE,GRID_SIZE)

        
        #create high_score
        high_score = HighScore(self.state.high_score,self.Img.high_score,screen,font)


        # print Img.player_right.get_rect().height, Img.stunned_right.get_rect().height
        #create player
        grid = Grid(SCREENRECT,gridsize, scale_x)
        player = Player(grid, self.Img)

        # qa,num_players = reset_board(screen,gridsize,font)
        qa,num_players,score,time_clock = self.game_start(screen,gridsize,font,started=0)

        # keep track of time
        clock = pygame.time.Clock()
        actor_facing = 1
        x_direction = 0
        y_direction = 0

        time = 0
        running = True

        while running:
            # Pump GTK messages.
            while Gtk.events_pending():
                Gtk.main_iteration()
            delta = clock.tick(25)
            time += delta
            if time > 1000:
                time = 0
                #self.Img.correct,screen,font
                time_clock.add(-1)
                if time_clock.get_ticks() == 0:
                    num_players.kill()
                    qa,num_players,score,time_clock = self.reset_board(screen,gridsize,
                                                       font,
                                                       num_players=num_players,
                                                       score=score)
                    self.state.update(lives=num_players.get_lives(),
                                 score=score.get_score(),
                                 time =time_clock.get_ticks())
                    high_score.set(self.state.high_score)

            events = pygame.event.get()
            for evt in events:
                if evt.type == pygame.QUIT:
                    self.save_state(PLAYER_LIVES, GAME_TIME)
                    running = False
                    #sys.exit(0)
                elif evt.type == pygame.KEYDOWN:
                    if evt.key == 27:
                        if not(self.running_sugar):
                            running = False
                            sys.exit(0)
                    # elif evt.key == pygame.K_SPACE:
                    if not evt.key in move_keys:
                        x = player.grid_position[0]
                        y = player.grid_position[1]
                        grid.draw_tile(x,y,screen)

                        #Pecking animation - 1st erase player,
                        #then set pecking image, then only update
                        #these dirtyrects, then delay
                        animate_dirtyrects = [player.erase(screen,grid.get_tile(x,y).get_background())]
                        player.set_image(self.Img.peck_right)
                        animate_dirtyrects.append(player.draw(screen))
                        pygame.display.update(animate_dirtyrects)
                        pygame.time.wait(200)

                        #try an answer
                        if (grid.get_tile(x,y).get_answer() == qa.get_correct_answer()):
                            peck_good.play()
                            score.add(1)

                            time_clock.set(GAME_TIME)
                            time_clock.update = 1
                            time = 0

                            if actor_facing == 1:
                                player.set_image(self.Img.happy_right)
                            else:
                                player.set_image(self.Img.happy_left)
                            #pygame.time.wait(850)
                            qa,num_players,score,time_clock = self.reset_board(screen,gridsize,
                                                               font,
                                                               num_players=num_players,
                                                               score=score,
                                                               time_clock=time_clock)
                            self.state.update(lives=num_players.get_lives(),
                                         score=score.get_score(),
                                         time =time_clock.get_ticks())
                            high_score.set(self.state.high_score)


                        else:
                            peck_bad.play()
                            num_players.kill()
                            time_clock.set(GAME_TIME)
                            time = 0

                            #probably right here
                            self.state.update(lives=num_players.get_lives(),
                                         time =time_clock.get_ticks())
                            high_score.set(self.state.high_score)



                            if actor_facing == 1:
                                player.set_image(self.Img.stunned_right)
                                player.set_rect_position(self.Img.stunned_right)
                            else:
                                player.set_image(self.Img.stunned_left)
                                player.set_rect_position(self.Img.stunned_left)

                    
                    elif evt.key == pygame.K_LEFT or evt.key == pygame.K_KP4:
                        bock.play()
                        x_direction = -1
                    elif evt.key == pygame.K_RIGHT or evt.key == pygame.K_KP6:
                        bock.play()
                        x_direction = 1
                    elif evt.key == pygame.K_DOWN or evt.key == pygame.K_KP2:
                        bock.play()
                        y_direction = 1
                    elif evt.key == pygame.K_UP or evt.key == pygame.K_KP8:
                        bock.play()
                        y_direction = -1
                elif evt.type == pygame.VIDEORESIZE:
                    pygame.display.set_mode(evt.size, pygame.RESIZABLE)

            if num_players.get_lives() <= 0:
                #reset the question
                # qa,num_players = reset_board(screen,gridsize,font)
                pygame.mixer.music.fadeout(2000)
                kuku_lose.play()
                qa,num_players,score,time_clock = self.game_over(screen,gridsize,font)
                self.state.update(lives=num_players.get_lives(),
                             score=score.get_score(),
                             time =time_clock.get_ticks())
                high_score.set(self.state.high_score)



            if self.state.won:
                pygame.mixer.music.fadeout(2000)
                kuku_win.play()
                pygame.mixer.music
                qa,num_players,score,time_clock = self.game_win(screen,gridsize,font)
                self.state.update(lives=num_players.get_lives(),
                             score=score.get_score(),
                             time =time_clock.get_ticks())
                self.state.won = 0
                high_score.set(self.state.high_score)


            # determine which direction the actor is facing
            if x_direction in [-1,1]:
                actor_facing = x_direction

            for actor in [player]:
                grid_pos = actor.grid_position
                # pygame.display.update(actor.erase(screen,
                #                               grid.get_tile(grid_pos[0],grid_pos[1]).get_background()))
                # pygame.display.update(grid.get_tile(grid_pos[0],grid_pos[1]).draw(screen))
                dirtyrects.extend(grid.get_tile(grid_pos[0],grid_pos[1]).draw(screen))
                dirtyrects.append(actor.erase(screen,
                                              grid.get_tile(grid_pos[0],grid_pos[1]).get_background()))

                actor.update()

            # old_position = player.grid_position
            player.move(x_direction,y_direction)
            x_direction = 0
            y_direction = 0

            #questions and answers
            dirtyrects.extend(qa.display_question(screen,font))
            qa.set_answers(screen,grid,font)
            dirtyrects.extend(grid.draw(screen))

            for actor in [player]:
                dirtyrects.append(actor.draw(screen))

            #lives
            dirtyrects.extend(num_players.draw_lives(screen))

            #score
            dirtyrects.extend(score.draw(screen))

            #high_score
            dirtyrects.extend(high_score.draw(screen))

            #time_clock
            dirtyrects.extend(time_clock.draw(screen))

            #do the update
            pygame.display.update(dirtyrects)
            dirtyrects = []

# def main():
#     pygame.init()
#     pygame.display.set_mode((0, 0), pygame.RESIZABLE)
#     k = KukuActivity(False)
#     k.run()

# if __name__ == '__main__':
#     main()
if __name__ == '__main__':
    pygame.init()
    pygame.display.set_mode((0, 0), pygame.RESIZABLE)
    k = KukuActivity(False)
    k.run()

