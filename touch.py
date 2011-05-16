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

from twisted.internet import reactor

pygame.init()


class FaldaCanvas(object):
    '''Main game'''

    def __init__(self):
        self.screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption('Client')
        self.FPS = 20
        self.counter = 0
        self.running = True
        self.boton_pulsado = False
        self.ultima_posicion = None
        self.cursors = pygame.sprite.Group()
        pygame.mouse.set_visible(False)
        #pygame.event.set_grab(True)
        self.board = pygame.Surface(self.get_screen_rect().size)

    def get_screen_center(self):
        return self.screen.get_rect().center

    def get_screen_rect(self):
        return self.screen.get_rect()

    def create_cursor(self, user, web_client=False):
        cursor = self.cursor_handler(self, user)
        self.cursors.add(cursor)
        if web_client:
            initial = (0, 0)
        else:
            initial = self.get_screen_center()
        cursor.rect = cursor.image.get_rect(topleft=initial)
        return cursor

    def loop(self):
        '''gets called every frame
        Gets user events, updates game state, and renders the game
        '''
        self.loop_actions()

        if self.running == True:
            reactor.callLater((1 / self.FPS), self.loop)
        else:
            reactor.stop()

    def loop_actions(self):
        # checking for user events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.client.send_click(event.button, True)
            if event.type == pygame.MOUSEBUTTONUP:
                self.client.send_click(event.button, False)
        rel = pygame.mouse.get_rel()
        if rel != (0, 0):
            self.client.send_move(*rel)

        self.screen.blit(self.board, (0, 0))
        self.cursors.draw(self.screen)
        pygame.display.flip()


class User(object):
    def __init__(self, ip_address, canvas, web_client=False):
        self.canvas = canvas
        self.ip_address = ip_address
        self.cursor = self.canvas.create_cursor(self, web_client)
