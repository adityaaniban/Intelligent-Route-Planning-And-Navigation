"""Performance measurement and comparison of search algorithms."""

import time

from algorithm import bfs, dfs, ucs, astar


def calculate_cost(graph, path):
    if not path:
        return None

    return sum(
        graph[path[i]][path[i + 1]]
        for i in range(len(path) - 1)
    )


def compare_algorithms(graph, start, goal, coordinates):

    searchers = {
        "BFS": lambda: bfs(graph, start, goal),
        "DFS": lambda: dfs(graph, start, goal),
        "UCS": lambda: ucs(graph, start, goal),
        "A*": lambda: astar(graph, start, goal, coordinates),
    }

    results = {}

    for name, search in searchers.items():

        start_time = time.perf_counter()

        path, explored_order = search()

        execution_time = time.perf_counter() - start_time

        distance = calculate_cost(graph, path)

        results[name] = {
            "path": path,
            "distance": distance,
            "explored_count": len(explored_order),
            "explored_order": explored_order,
            "execution_time": execution_time,
            "execution_time_ms": execution_time * 1000,
            "cities_in_route": len(path),
            "edges_in_route": max(0, len(path) - 1),
            "status": "Success" if path else "No route",
        }

    return results