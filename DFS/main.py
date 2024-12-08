import sys
import os
import time

## importa classes
from vs.environment import Env
from explorer import Explorer
from rescuer import Rescuer
from map import Map  

def main(data_folder_name):
    current_folder = os.path.abspath(os.getcwd())
    data_folder = os.path.abspath(os.path.join(current_folder, data_folder_name))

    # Instancia o ambiente
    env = Env(data_folder)
    
    # Cria um mapa global compartilhado
    shared_map = Map()
    
    # Configura os agentes
    rescuer_file = os.path.join(data_folder, "rescuer_config.txt")
    resc = Rescuer(env, rescuer_file,shared_map)
    
    num_explorers = 4  # Número de exploradores
    explorers = []
    for i in range(num_explorers):
        explorer_config_file = os.path.join(data_folder, f"explorer_{i}_config.txt")
        print(f"Config file for explorer {i}: {explorer_config_file}")
        explorer = Explorer(env, explorer_config_file, resc, shared_map)  # Passa o mapa compartilhado
        explorers.append(explorer)

    # Executa o simulador
    env.run()

if __name__ == '__main__':
    """ To get data from a different folder than the default called data
    pass it by the argument line"""
    
    if len(sys.argv) > 1:
        data_folder_name = sys.argv[1]
    else:
        data_folder_name = os.path.join("datasets", "data_42v_20x20")
        
    main(data_folder_name)
