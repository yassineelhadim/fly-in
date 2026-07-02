Dijkstra is an algorithm that finds the shortest path from a starting node to all other nodes by repeatedly exploring the closest unvisited node.


Steps:
  - Set start to 0 and all the other nodes to infinity
  - Repeatedly pick the univisited node with the smallest distance
  - Check all its neighbors and see if going through it gives a shorter path
  - Mark the node as visited so it's ignored