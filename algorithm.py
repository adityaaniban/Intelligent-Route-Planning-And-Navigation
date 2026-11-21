"""BFS, DFS, Uniform Cost Search, and A* implementations."""
from collections import deque
import heapq
import itertools
import math


def reconstruct_path(parent, goal):
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent[current]
    return list(reversed(path))


def bfs(graph, start, goal):
    """Find a route with the fewest edges; not necessarily least distance."""
    queue = deque([start])
    visited = {start}
    parent = {start: None}
    explored = []

    while queue:
        current = queue.popleft()
        explored.append(current)
        if current == goal:
            return reconstruct_path(parent, goal), explored

        for neighbour in graph[current]:
            if neighbour not in visited:
                visited.add(neighbour)
                parent[neighbour] = current
                queue.append(neighbour)

    return [], explored


def dfs(graph, start, goal):
    """Depth-first route search; does not guarantee an optimal route."""
    stack = [start]
    visited = {start}
    parent = {start: None}
    explored = []

    while stack:
        current = stack.pop()
        explored.append(current)
        if current == goal:
            return reconstruct_path(parent, goal), explored

        for neighbour in reversed(list(graph[current])):
            if neighbour not in visited:
                visited.add(neighbour)
                parent[neighbour] = current
                stack.append(neighbour)

    return [], explored


def ucs(graph, start, goal):
    """Find a minimum-cost route for non-negative edge weights."""
    counter = itertools.count()
    queue = [(0, next(counter), start)]
    parent = {start: None}
    best_cost = {start: 0}
    explored = []

    while queue:
        current_cost, _, current = heapq.heappop(queue)
        if current_cost != best_cost[current]:
            continue

        explored.append(current)
        if current == goal:
            return reconstruct_path(parent, goal), explored

        for neighbour, distance in graph[current].items():
            new_cost = current_cost + distance
            if new_cost < best_cost.get(neighbour, math.inf):
                best_cost[neighbour] = new_cost
                parent[neighbour] = current
                heapq.heappush(
                    queue, (new_cost, next(counter), neighbour)
                )

    return [], explored


def haversine(city1, city2, coordinates):
    """Straight-line distance between two coordinates, in kilometres."""
    lat1, lon1 = coordinates[city1]
    lat2, lon2 = coordinates[city2]
    radius = 6371.0
    lat1, lon1, lat2, lon2 = map(
        math.radians, (lat1, lon1, lat2, lon2)
    )
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(a))


def make_admissible_scale(graph, coordinates):
    """
    Scale straight-line distance conservatively so the heuristic is
    admissible for this road graph.
    """
    ratios = []
    for city1, neighbours in graph.items():
        for city2, road_distance in neighbours.items():
            if city1 < city2:
                straight = haversine(city1, city2, coordinates)
                if straight > 0:
                    ratios.append(road_distance / straight)
    return min(1.0, min(ratios)) * 0.99 if ratios else 0.0


def astar(graph, start, goal, coordinates):
    """A* with f(n) = g(n) + h(n)."""
    scale = make_admissible_scale(graph, coordinates)

    def heuristic(city):
        return scale * haversine(city, goal, coordinates)

    counter = itertools.count()
    queue = [(heuristic(start), 0, next(counter), start)]
    parent = {start: None}
    best_cost = {start: 0}
    explored = []

    while queue:
        _, current_cost, _, current = heapq.heappop(queue)
        if current_cost != best_cost[current]:
            continue

        explored.append(current)
        if current == goal:
            return reconstruct_path(parent, goal), explored

        for neighbour, distance in graph[current].items():
            new_cost = current_cost + distance
            if new_cost < best_cost.get(neighbour, math.inf):
                best_cost[neighbour] = new_cost
                parent[neighbour] = current
                priority = new_cost + heuristic(neighbour)
                heapq.heappush(
                    queue, (priority, new_cost, next(counter), neighbour)
                )

    return [], explored
