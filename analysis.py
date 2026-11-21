"""Performance measurement and comparison for the search algorithms."""
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
        elapsed = time.perf_counter() - start_time

        results[name] = {
            "path": path,
            "distance": calculate_cost(graph, path),
            "explored_count": len(explored_order),
            "explored_order": explored_order,
            "execution_time": elapsed,
        }
    print(results)
    return results
