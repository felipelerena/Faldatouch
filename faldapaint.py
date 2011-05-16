#!/usr/bin/env python
"""
 This file is part of FaldaTouch.

    Faldatouch is a framework to add multi-pointer support to pygame
    applications
    Copyright (C) 2011 Felipe Lerena, Alejandro Cura, Hugo Ruscitti

    FaldaTouch is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    FaldaTouch is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with FaldaTouch.  If not, see <http://www.gnu.org/licenses/>.
"""
import pygame

from random import choice

from touch import User, FaldaCanvas
from server import start


BLUE = (0, 128, 255)
WHITE = (255, 255, 255)
GREEN = (64, 192, 128)

FRIENDLY_COLORS = [
   (0, 128, 255),
   (0, 0, 0),
   (255, 255, 255),
   (255, 0, 0),
   (255, 255, 0),
   (255, 0, 255),
   (0, 255, 255)
   ]


class Canvas(FaldaCanvas):
    def __init__(self):
        super(Canvas, self).__init__()

        self.board.fill(GREEN)
        font = pygame.font.Font(None, 48)
        repourl = "hg clone http://192.168.1.119:8000 faldatouch"
        texto = font.render(repourl, True, WHITE)
        self.board.blit(texto, texto.get_rect(midbottom=self.get_screen_rect().center))

        self._paint_background()

        self.cursor_handler = SpriteCursor
        self.user_class = FaldaPaintUser

    def draw_line(self, pos1, pos2, color=WHITE):
        pygame.draw.line(self.board, color, pos1, pos2)

    def borrar(self, pos1, pos2, color=GREEN):
        pygame.draw.line(self.board, color, pos1, pos2, 64)

    def _paint_background(self):
        background_color = pygame.Surface(self.screen.get_size()).convert()
        background_color.fill((200, 200, 200))
        self.screen.blit(background_color, (0, 0))

class SpriteCursor(pygame.sprite.Sprite):
    def __init__(self, canvas, user):
        super(SpriteCursor, self).__init__()
        self.image = pygame.image.load('cursor.png').convert_alpha()
        self.canvas = canvas
        self.user = user
        self.color = choice(FRIENDLY_COLORS)

    def relative_move(self, dx, dy):
        old_position = self.rect.topleft
        self.rect.move_ip(dx, dy)
        self.rect.clamp_ip(self.canvas.get_screen_rect())
        new_position = self.rect.topleft
        if self.user.drawing:
            self.canvas.draw_line(old_position, new_position, self.color)
        if self.user.deleting:
            self.canvas.borrar(old_position, new_position)


class FaldaPaintUser(User):
    def __init__(self, ip_address, canvas, web_client=False):
        super(FaldaPaintUser, self).__init__(ip_address, canvas, web_client)
        self.drawing = False
        self.deleting = False

    def handle_mouse(self, estado, dx, dy):
        self.cursor.relative_move(dx, dy)

    def handle_leftbutton(self, estado):
        self.deleting = False
        self.drawing = estado == 0 #presionado

    def handle_rightbutton(self, estado):
        self.drawing = False
        self.deleting = estado == 0 #presionado

    def handle_middlebutton(self, estado):
        self.cursor.color = choice(FRIENDLY_COLORS)


if __name__ == "__main__":
    canvas = Canvas()
    start(canvas, "localhost")

