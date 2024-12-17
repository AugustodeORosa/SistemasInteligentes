import sys
import os
import random
import math
import queue
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
    total_explorers = 0  # Número total de exploradores
    completed_explorers = 0  # Contador de exploradores que finalizaram
    victim_global_id = 0  # ID único para todas as vítimas

    def __init__(self, env, config_file, resc, shared_map, ex_id):
        super().__init__(env, config_file)
        self.walk_stack = Stack()
        self.set_state(VS.ACTIVE)  # Certifica que o estado inicial é ACTIVE
        self.resc = resc
        self.x = 0
        self.y = 0
        self.map = shared_map
        self.victims = {}
        self.id = ex_id

        # Incrementa o número total de exploradores
        Explorer.total_explorers += 1
      

        # Inicializa o mapa com a posição inicial
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())
        self.map.add_visited((self.x,self.y))



    def finalize_map(self):
        """ Finaliza a exploração e verifica se todos os exploradores concluíram. """
        print(f"{self.NAME}: Finalizando exploração e compartilhando o mapa.")
        for coord, data in self.map.map_data.items():
            if not self.resc.map.in_map(coord):
                self.resc.map.add(coord, *data)

        # Adiciona vítimas ao mapa global
        for victim_id, (victim_coord, victim_data) in self.victims.items():
            # Verifica se a vítima já está no mapa global
            if not self.resc.map.in_map(victim_coord):
                # Obtém informações completas da vítima para inclusão no mapa global
                difficulty, _, actions_res = self.map.get(victim_coord)
                self.resc.map.add(victim_coord, difficulty, victim_id, actions_res)
                print(f"{self.NAME}: Vítima adicionada no mapa global na posição {victim_coord} com ID único {victim_id}.")
            else:
                # Verifica se o ID da vítima já está correto no mapa global
                existing_data = self.resc.map.get(victim_coord)
                if existing_data[1] != victim_id:
                    print(f"{self.NAME}: Corrigindo informações da vítima no mapa global na posição {victim_coord}.")
                    difficulty, _, actions_res = self.map.get(victim_coord)
                    self.resc.map.add(victim_coord, difficulty, victim_id, actions_res)
                else:
                    print(f"{self.NAME}: Vítima na posição {victim_coord} já registrada no mapa global com ID {victim_id}.")

        Explorer.completed_explorers += 1
        print(f"Exploradores concluídos: {Explorer.completed_explorers}/{Explorer.total_explorers}")
        if Explorer.completed_explorers == Explorer.total_explorers:
            print("Todos os exploradores retornaram à base. Chamando o resgatador.")
            self.map.draw()
            self.resc.go_save_victims(self.map, {})



    def explore(self):
        """ Implementa DFS on-line para explorar o ambiente. """
        current_pos = (self.x, self.y)
        obstacles = self.check_walls_and_lim()
        unvisited_neighbors = ()

        # Encontra vizinhos não visitados
        match self.id:
            case 0:
                #explorador do quadrante 1(esquerda-cima)
                #colocar os lados da direção enviasada escolhida primeiro
                #para que ele vá o máximo possivel para o lado dele antes de explorar

                RNG = random.randint(0,100)
                if(0 <= RNG <= 20):
                    direction = 7 #ul
                elif(21 <= RNG <= 40):
                    direction = 0 #up
                elif(41 <= RNG <= 60):
                    direction = 6 #left
                elif(61 <= RNG <= 65):
                    direction = 4 # down
                elif(66 <= RNG <= 70):
                    direction = 2 #right
                elif(71 <= RNG <= 80):
                    direction = 1
                elif(81 <= RNG <= 90):
                    direction = 3
                elif(91 <= RNG <= 100):
                    direction = 5

            case 1:
                #explorador do quadrante 2(direita-cima)

                RNG = random.randint(0,100)
                if(0 <= RNG <= 20):
                    direction = 1 #ul
                elif(21 <= RNG <= 40):
                    direction = 0 #up
                elif(41 <= RNG <= 60):
                    direction = 2 #left
                elif(61 <= RNG <= 65):
                    direction = 4 # down
                elif(66 <= RNG <= 70):
                    direction = 6 #right
                elif(71 <= RNG <= 80):
                    direction = 3
                elif(81 <= RNG <= 90):
                    direction = 5
                elif(91 <= RNG <= 100):
                    direction = 7

            case 2:
                #explorador do quadrante 3(esquerda-baixo)

                RNG = random.randint(0,100)
                if(0 <= RNG <= 20):
                    direction = 5 #dl
                elif(21 <= RNG <= 40):
                    direction = 4 #down
                elif(41 <= RNG <= 60):
                    direction = 6 #left
                elif(61 <= RNG <= 65):
                    direction = 0 #up
                elif(66 <= RNG <= 70):
                    direction = 2 #right
                elif(71 <= RNG <= 80):
                    direction = 1
                elif(81 <= RNG <= 90):
                    direction = 3
                elif(91 <= RNG <= 100):
                    direction = 7

            case 3:
                #explorador do quadrante 4(direita-baixo)  

                RNG = random.randint(0,100)
                if(0 <= RNG <= 20):
                    direction = 3 #dr
                elif(21 <= RNG <= 40):
                    direction = 4 #d
                elif(41 <= RNG <= 60):
                    direction = 2 #right    
                elif(61 <= RNG <= 65):
                    direction = 0 
                elif(66 <= RNG <= 70):
                    direction = 6 
                elif(71 <= RNG <= 80):
                    direction = 1
                elif(81 <= RNG <= 90):
                    direction = 7
                elif(91 <= RNG <= 100):
                    direction = 5

        nx = (self.x + Explorer.AC_INCR[direction][0])
        ny = (self.y + Explorer.AC_INCR[direction][1])

        is_v = self.map.return_visited((nx, ny))
        
        if not is_v:
            # Escolhe o primeiro vizinho não visitado
            result = self.walk(*Explorer.AC_INCR[direction])

            if result == VS.EXECUTED:
                #elf.walk_stack.push((self.x, self.y))  # Salva posição atual
                self.walk_stack.push((self.x, self.y))  # Salva posição atual
                self.x, self.y = nx, ny
                self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())
                self.map.add_visited((self.x, self.y))

                # Verifica por vítimas
                seq = self.check_for_victim()
                if seq != VS.NO_VICTIM:
                    vs = self.read_vital_signals()
                    victim_id = Explorer.victim_global_id  # Atribui um ID global único
                    Explorer.victim_global_id += 1         # Incrementa o ID global
                    self.victims[victim_id] = ((self.x, self.y), vs)
                    print(f"{self.NAME}: Vítima encontrada em ({self.x}, {self.y}) com ID único {victim_id} pelo explorador {self.id}.")
        else:
            # Retrocede
            if not self.walk_stack.is_empty():
                prev_x, prev_y = self.walk_stack.pop()
                dx, dy = prev_x - self.x, prev_y - self.y
                self.walk(dx, dy)
                self.x, self.y = prev_x, prev_y
            else:
                direction = random.randint(0, 7)
            
            if obstacles[direction] == VS.CLEAR:
                nx = (self.x + Explorer.AC_INCR[direction][0])
            ny = (self.y + Explorer.AC_INCR[direction][1])
            result = self.walk(*Explorer.AC_INCR[direction])

            if result == VS.EXECUTED:
                #elf.walk_stack.push((self.x, self.y))  # Salva posição atual
                self.x, self.y = nx, ny

                # Verifica por vítimas
                seq = self.check_for_victim()
                if seq != VS.NO_VICTIM:
                    vs = self.read_vital_signals()
                    victim_id = Explorer.victim_global_id  # Atribui um ID global único
                    Explorer.victim_global_id += 1         # Incrementa o ID global
                    self.victims[victim_id] = ((self.x, self.y), vs)
                    print(f"{self.NAME}: Vítima encontrada em ({self.x}, {self.y}) com ID único {victim_id} pelo explorador {self.id}.")




    def come_back(self):
        """ Retorna para a base utilizando a pilha de movimentos. """
        if not self.walk_stack.is_empty():
            prev_x, prev_y = self.walk_stack.pop()
            dx, dy = prev_x - self.x, prev_y - self.y
            result = self.walk(dx, dy)
            if result == VS.EXECUTED:
                self.x += dx
                self.y += dy
        elif (self.x == 0 and self.y == 0):
            print(f"{self.NAME}: Retornou à base.")
            self.finalize_map()
            self.set_state(VS.IDLE)
            return False
        else:
            print(f"{self.NAME}: Pilha vazia, mas ainda não está na base.")

    def deliberate(self) -> bool:
        """ Escolhe a próxima ação para o explorador. """
        # Verifica se o explorador está ativo
        if self.get_state() != VS.ACTIVE:
            print(f"{self.NAME}: Estado inativo. Não há mais ações a realizar.")
            return False

        # Verifica se ainda há tempo para explorar
        if self.get_rtime() > 0:
            self.explore()
            return True

        print(f"{self.NAME}: Verificando condições para chamar o resgatador.")
        print(f"{self.NAME}: Pilha vazia? {self.walk_stack.is_empty()}")
        print(f"{self.NAME}: Está na base? (x: {self.x}, y: {self.y}) -> {(self.x == 0 and self.y == 0)}")
        print(f"{self.NAME}: Tempo restante: {self.get_rtime()}")

        # Se não há mais tempo, mas não está na base, tenta voltar
        if self.walk_stack.is_empty():
            print(f"{self.NAME}: Sem mais movimentos possíveis. Tentando voltar à base.")
            self.come_back()
            return True

        self.come_back()
        return True
