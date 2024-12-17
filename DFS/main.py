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
    
    # Cria os mapas de cada explorador
    shared_map = Map()
    shared_map_0 = Map()
    shared_map_1 = Map()
    shared_map_2 = Map()
    shared_map_3 = Map()

    # Configura os agentes
    rescuer_file = os.path.join(data_folder, "rescuer_config.txt")
    resc = Rescuer(env, rescuer_file,shared_map)
    
    num_explorers = 4  # Número de exploradores
    explorers = []
    for i in range(num_explorers):
        explorer_config_file = os.path.join(data_folder, f"explorer_{i}_config.txt")
        print(f"Config file for explorer {i}: {explorer_config_file}")
        match i:
            case 0:
                explorer = Explorer(env, explorer_config_file, resc, shared_map_0, 0)  # Passa o mapa
            case 1:
                explorer = Explorer(env, explorer_config_file, resc, shared_map_1, 1)
            case 2:
                explorer = Explorer(env, explorer_config_file, resc, shared_map_2, 2)
            case 3:
                explorer = Explorer(env, explorer_config_file, resc, shared_map_3, 3)    
        explorers.append(explorer)

    # Executa o simulador
    env.run()

if __name__ == '__main__':
    """ To get data from a different folder than the default called data
    pass it by the argument line"""
    
    if len(sys.argv) > 1:
        data_folder_name = sys.argv[1]
    else:
        data_folder_name = os.path.join("datasets", "data_400v_90x90")
        
    main(data_folder_name)
