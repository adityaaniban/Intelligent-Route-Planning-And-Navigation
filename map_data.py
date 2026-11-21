"""City graph and map visualization."""
import networkx as nx
import matplotlib.pyplot as plt

# Coordinates are (latitude, longitude).
CITIES = {
    "Chennai": (13.0827, 80.2707),
    "Vellore": (12.9165, 79.1325),
    "Tirupati": (13.6288, 79.4192),
    "Bengaluru": (12.9716, 77.5946),
    "Hosur": (12.7409, 77.8253),
    "Krishnagiri": (12.5186, 78.2137),
    "Salem": (11.6643, 78.1460),
    "Coimbatore": (11.0168, 76.9558),
}

# Illustrative road distances in km, not live navigation data.
ROADS = [
    ("Chennai", "Vellore", 140),
    ("Chennai", "Tirupati", 135),
    ("Vellore", "Tirupati", 110),
    ("Vellore", "Bengaluru", 215),
    ("Vellore", "Krishnagiri", 180),
    ("Tirupati", "Bengaluru", 255),
    ("Bengaluru", "Hosur", 40),
    ("Bengaluru", "Krishnagiri", 90),
    ("Hosur", "Salem", 165),
    ("Krishnagiri", "Salem", 90),
    ("Salem", "Coimbatore", 165),
]


def build_graph(blocked_roads=None):
    """Build an undirected weighted graph, excluding blocked roads."""
    blocked = {frozenset(edge) for edge in (blocked_roads or [])}
    graph = {city: {} for city in CITIES}
    for city1, city2, distance in ROADS:
        if frozenset((city1, city2)) not in blocked:
            graph[city1][city2] = distance
            graph[city2][city1] = distance
    return graph


def create_map_figure(graph, route=None, explored=None, blocked_roads=None):
    """Return a Matplotlib figure for display in Streamlit."""
    route = route or []
    explored = set(explored or [])
    blocked_roads = blocked_roads or []

    road_graph = nx.Graph()
    road_graph.add_nodes_from(CITIES)
    for city1, neighbours in graph.items():
        for city2, distance in neighbours.items():
            road_graph.add_edge(city1, city2, weight=distance)

    positions = {
        city: (lon, lat) for city, (lat, lon) in CITIES.items()
    }
    fig, ax = plt.subplots(figsize=(11, 7))

    nx.draw_networkx_edges(
        road_graph, positions, edge_color="gray", width=2, ax=ax
    )

    # Show blocked roads as red dashed lines.
    for city1, city2 in blocked_roads:
        x = [positions[city1][0], positions[city2][0]]
        y = [positions[city1][1], positions[city2][1]]
        ax.plot(x, y, color="red", linestyle="--", linewidth=2)

    normal = [c for c in CITIES if c not in explored and c not in route]
    explored_only = [c for c in CITIES if c in explored and c not in route]

    nx.draw_networkx_nodes(
        road_graph, positions, nodelist=normal,
        node_color="lightblue", node_size=850, ax=ax
    )
    nx.draw_networkx_nodes(
        road_graph, positions, nodelist=explored_only,
        node_color="gold", node_size=900, ax=ax
    )

    if route:
        nx.draw_networkx_edges(
            road_graph, positions, edgelist=list(zip(route, route[1:])),
            edge_color="blue", width=4, ax=ax
        )
        if len(route) > 2:
            nx.draw_networkx_nodes(
                road_graph, positions, nodelist=route[1:-1],
                node_color="lightgreen", node_size=950, ax=ax
            )
        nx.draw_networkx_nodes(
            road_graph, positions, nodelist=[route[0]],
            node_color="green", node_size=1050, ax=ax
        )
        if len(route) > 1:
            nx.draw_networkx_nodes(
                road_graph, positions, nodelist=[route[-1]],
                node_color="tomato", node_size=1050, ax=ax
            )

    nx.draw_networkx_labels(
        road_graph, positions, font_size=9, font_weight="bold", ax=ax
    )
    nx.draw_networkx_edge_labels(
        road_graph, positions,
        edge_labels=nx.get_edge_attributes(road_graph, "weight"),
        font_size=8, ax=ax
    )

    ax.set_title("South Indian Demonstration Road Network")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    return fig
