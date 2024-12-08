# EXPLORER AGENT
# 
#
###
### 

import sys
import os
import random
import math
from abc import ABC, abstractmethod
from vs.abstract_agent import AbstAgent
from vs.constants import VS
from map import Map

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()

    def is_empty(self):
        return len(self.items) == 0
class Explorer(AbstAgent):
    def __init__(self, env, config_file, resc, shared_map):
        super().__init__(env, config_file)
        self.walk_stack = Stack()
        self.set_state(VS.ACTIVE)
        self.resc = resc
        self.x = 0
        self.y = 0
        self.map = shared_map  # Usa o mapa compartilhado
        self.victims = {}
        
        # Adiciona a posição inicial (base) ao mapa
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())


    def explore(self):
        """ Implementa DFS on-line para explorar o ambiente. """
        current_pos = (self.x, self.y)
        obstacles = self.check_walls_and_lim()
        
        # Encontra vizinhos não visitados
        unvisited_neighbors = []
        for direction, result in enumerate(obstacles):
            if result == VS.CLEAR:  # Considera apenas direções acessíveis
                neighbor = (self.x + Explorer.AC_INCR[direction][0], 
                            self.y + Explorer.AC_INCR[direction][1])
                if not self.map.in_map(neighbor):  # Não visitado ainda
                    unvisited_neighbors.append((direction, neighbor))
        
        if unvisited_neighbors:
            # Escolhe o primeiro vizinho não visitado (DFS)
            direction, (nx, ny) = unvisited_neighbors[0]
            
            # Move para o vizinho
            result = self.walk(*Explorer.AC_INCR[direction])
            if result == VS.EXECUTED:
                # Adiciona a posição atual à pilha
                self.walk_stack.push((self.x, self.y))
                
                # Atualiza a posição
                self.x, self.y = nx, ny
                
                # Atualiza o mapa
                self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())
                
                # Verifica por vítimas
                seq = self.check_for_victim()
                if seq != VS.NO_VICTIM:
                    vs = self.read_vital_signals()
                    self.victims[vs[0]] = ((self.x, self.y), vs)
                    print(f"{self.NAME}: Vítima encontrada em ({self.x}, {self.y})")
        else:
            # Sem vizinhos não visitados, retrocede
            if not self.walk_stack.is_empty():
                prev_x, prev_y = self.walk_stack.pop()
                dx, dy = prev_x - self.x, prev_y - self.y
                self.walk(dx, dy)
                self.x, self.y = prev_x, prev_y
            else:
                # Condição final de exploração
                print(f"{self.NAME}: Sem mais movimentos possíveis, exploração finalizada.")
                self.set_state(VS.IDLE)  # Marca o agente como inativo
                
    def come_back(self):
        """ Retorna para a base utilizando a pilha de movimentos. """
        if not self.walk_stack.is_empty():
            dx, dy = self.walk_stack.pop()
            dx = dx * -1
            dy = dy * -1
            result = self.walk(dx, dy)
            if result == VS.EXECUTED:
                self.x += dx
                self.y += dy
        elif (self.x == 0 and self.y == 0):
            print(f"{self.NAME}: Retornou à base.")

    def deliberate(self) -> bool:
        """ Escolhe a próxima ação para o explorador. """
        # Verifica se o explorador ainda está ativo
        if self.get_state() != VS.ACTIVE:
            return False

        consumed_time = self.TLIM - self.get_rtime()
        if consumed_time < self.get_rtime():
            self.explore()
            return True

        # Hora de retornar à base
        if self.walk_stack.is_empty() or (self.x == 0 and self.y == 0):
            print(f"{self.NAME}: rtime {self.get_rtime()}, chamando o resgatador")
            self.resc.go_save_victims(self.map, self.victims)  # Chama o resgatador
            self.set_state(VS.IDLE)  # Marca o explorador como inativo após o chamado
            return False

        self.come_back()
        return True