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


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import sugargame.canvas
from sugar3.activity import activity
from gettext import gettext as _

from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.graphics.toolbutton import ToolButton
import pygame
import kuku

class Activity(activity.Activity):

    def __init__(self, handle):
        # activity.Activity.__init__(self, handle)
        # self.game = kuku.KukuActivity()
        # self.build_toolbar()
        # self._pygamecanvas = sugargame.canvas.PygameCanvas(self)
        # self.set_canvas(self._pygamecanvas)
        # self._pygamecanvas.grab_focus()
        # self._pygamecanvas.run_pygame(self.game.run)
        activity.Activity.__init__(self, handle)
        self.game = kuku.KukuActivity()
        self.build_toolbar()
        self._pygamecanvas = sugargame.canvas.PygameCanvas(self)
    #    self._pygamecanvas = sugargame.canvas.PygameCanvas(self,main=self.game.run, modules=[pygame.display])
        self.set_canvas(self._pygamecanvas)
        self._pygamecanvas.run_pygame(self.game.run)
        self._pygamecanvas.grab_focus()
        
    def build_toolbar(self):

        toolbox = ToolbarBox()
        activity_button = ActivityToolbarButton(self)
        toolbox.toolbar.insert(activity_button, -1)
        activity_button.show()

        barra = toolbox.toolbar

        separator2 = Gtk.SeparatorToolItem()
        separator2.props.draw = False
        separator2.set_expand(True)
        barra.insert(separator2, -1)

        stop_button = StopButton(self)
        stop_button.props.accelerator = '<Ctrl>q'
        barra.insert(stop_button, -1)
        stop_button.show()

        self.set_toolbar_box(toolbox)

        toolbox.show_all()


    def read_file(self, file_path):
        pass

    def write_file(self, file_path):
        pass

