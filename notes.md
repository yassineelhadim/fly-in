current = start node

while there are unvisited nodes:

    Mark current as visited.

    Look at all neighbors of current.

    For each neighbor:
        - Skip it if it's blocked or already visited.
        - Compute the cost of reaching it through current.
        - If this cost is smaller than its current distance:
            - Update its distance.
            - Set previous[neighbor] = current.

    Find the unvisited node with the smallest distance.

    et current to that node.