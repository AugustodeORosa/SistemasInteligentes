# Online DFS Explorer and a DFS Rescuer

This example features an explorer agent that uses Online Depth-First Search (DFS) to navigate the environment systematically. It constructs a map of the explored region containing the obstacles and victims. The explorer then passes the map to the rescuer. Subsequently, the rescuer walks using the depth-first search within the discovered region, attempting to rescue the found victims.

## Key Updates
- The explorer agent now employs Online DFS instead of random exploration.
- Improved victim discovery rate with systematic navigation.
- The rescuer agent continues to use DFS to save the victims efficiently.

## How to Use
1. Copy the `explorer.py`, `rescuer.py`, and `main.py` to a folder.
2. Place all accessory `.py` files you create into the same folder.
3. Copy the folder `vs` into the folder.

## Expected Folder Structure
```
* folder
  * main.py
  * rescuer.py
  * explorer.py
  * vs
    * abstract_agent.py
    * constants.py
    * environment.py
    * physical_agent.py
```

