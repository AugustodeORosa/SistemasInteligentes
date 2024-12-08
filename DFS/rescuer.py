##  RESCUER AGENT
### @Author: Tacla (UTFPR)
### Demo of use of VictimSim
### Improved version with synchronized map updates and enhanced planning logic.

import os
import random
from map import Map
from vs.abstract_agent import AbstAgent
from vs.physical_agent import PhysAgent
from vs.constants import VS
from abc import ABC, abstractmethod

## Classe que define o Agente Rescuer com um plano fixo
class Rescuer(AbstAgent):
    def __init__(self, env, config_file,shared_map):
        """
        @param env: a reference to an instance of the environment class
        @param config_file: the absolute path to the agent's config file"""
        super().__init__(env, config_file)

        # Specific initialization for the rescuer
        self.map = shared_map
        self.victims = None         # List of found victims
        self.plan = []              # A list of planned actions
        self.plan_x = 0             # X position during planning
        self.plan_y = 0             # Y position during planning
        self.plan_visited = set()   # Positions already planned to visit
        self.plan_rtime = self.TLIM # Remaining time during planning
        self.plan_walk_time = 0.0   # Previewed time to walk during rescue
        self.x = 0                  # Current X position during execution
        self.y = 0                  # Current Y position during execution

        # Starts in IDLE state.
        self.set_state(VS.IDLE)

    def update_map(self, map, victims):
        """
        Updates the shared map with data sent by explorers.
        @param map: The shared map with visited positions
        @param victims: The list of victims found in the exploration
        """
        self.map = map
        self.victims = victims
        print(f"{self.NAME}: Mapa atualizado com {len(self.victims)} vítimas.")

    def go_save_victims(self, map, victims):
        print(f"\n\n*** R E S C U E R ***")
        self.map = map
        print(f"{self.NAME} Mapa recebido do explorador")
        self.map.draw()

        self.victims = victims
        print(f"{self.NAME} Total de vítimas encontradas: {len(self.victims)}")

        # Cria o plano de resgate
        self.__planner()
        self.set_state(VS.ACTIVE)

    def __depth_search(self, actions_res):
        enough_time = True
        for i, ar in enumerate(actions_res):
            if ar != VS.CLEAR:
                continue

            # Planning the walk
            dx, dy = Rescuer.AC_INCR[i]
            target_xy = (self.plan_x + dx, self.plan_y + dy)

            # Verifications
            if not self.map.in_map(target_xy):
                continue
            if target_xy in self.plan_visited:
                continue

            # Update planning variables
            self.plan_x += dx
            self.plan_y += dy
            difficulty, vic_seq, next_actions_res = self.map.get((self.plan_x, self.plan_y))
            step_cost = (self.COST_LINE if dx == 0 or dy == 0 else self.COST_DIAG) * difficulty

            if self.plan_walk_time + step_cost > self.plan_rtime:
                enough_time = False

            if enough_time:
                self.plan_walk_time += step_cost
                self.plan_rtime -= step_cost
                self.plan_visited.add((self.plan_x, self.plan_y))
                if vic_seq == VS.NO_VICTIM:
                    self.plan.append((dx, dy, False))
                elif vic_seq != VS.NO_VICTIM:
                    if self.plan_rtime - self.COST_FIRST_AID >= self.plan_walk_time:
                        self.plan.append((dx, dy, True))
                        self.plan_rtime -= self.COST_FIRST_AID
                    else:
                        enough_time = False

                if enough_time:
                    self.__depth_search(next_actions_res)
                else:
                    return

    def __planner(self):
        """ Generates a rescue plan using DFS and ensures return to base. """
        self.plan_visited.add((0, 0))  # Always start at the base
        difficulty, vic_seq, actions_res = self.map.get((0, 0))
        self.__depth_search(actions_res)

        # Plan return to the base
        come_back_plan = [(a[0] * -1, a[1] * -1, False) for a in reversed(self.plan)]
        self.plan += come_back_plan

    def deliberate(self) -> bool:
        """ Executes planned actions. """
        if not self.plan:
            return False

        dx, dy, there_is_vict = self.plan.pop(0)
        walked = self.walk(dx, dy)

        if walked == VS.EXECUTED:
            self.x += dx
            self.y += dy
            if there_is_vict and self.first_aid():
                print(f"{self.NAME} Vítima resgatada em ({self.x}, {self.y})")
            elif there_is_vict:
                print(f"{self.NAME} Plano falhou - vítima não encontrada em ({self.x}, {self.y})")
        else:
            print(f"{self.NAME} Plano falhou - erro ao caminhar na posição ({self.x}, {self.y})")

        return True
