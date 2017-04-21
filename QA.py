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

# QA class containing basic questions and answers.

import re
import random

class QA(object):
    
    def __init__(self):
        self.false_answers = []
        self.false_function = 0
    
    def set_question(self, question_string):
        """set question with spaces separating operators and numbers
        """
        p = re.compile(r'([0-9]*)([+-/*])([0-9]*)')
        new =  p.sub(r'\1 \2 \3',question_string)
        self.question = ' '.join(re.split('\s+',new))
    
    def get_question(self):
        return self.question
    
    def set_correct_answer(self,answer):
        self.correct_answer = answer
    
    def get_correct_answer(self):
        return self.correct_answer
    
    def set_false_answer(self,answer):
        if type(answer) == type(1):
            self.false_answers.append(answer)
        elif type(answer) == type([]):
            self.false_answers.extend(answer)
    
    def set_false_function(self,function):
        self.false_function = function
    
    def get_false_answer(self):
        if self.false_function:
            return self.false_function(self.get_correct_answer())
        else:
            return random.choice(self.false_answers)