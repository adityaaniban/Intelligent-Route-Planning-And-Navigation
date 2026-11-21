"""Streamlit web application. Run with: streamlit run main.py"""
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from map_data import CITIES, ROADS, build_graph, create_map_figure
from algorithm import bfs, dfs, ucs, astar
from analysis import compare_algorithms, calculate_cost


st.set_page_config(
    page_title="Intelligent Route Planner",
    page_icon="🗺️",
    layout="wide",
)

st.title("🗺️ Intelligent Route Planning System")
st.caption(
    "AI search algorithms for a demonstration road network "
    "of selected South Indian cities."
)

with st.sidebar:
    st.header("Navigation Settings")
    city_names = list(CITIES)
    start = st.selectbox("Starting city", city_names, index=0)
    goal = st.selectbox("Destination city", city_names, index=3)

    algorithm_name = st.selectbox(
        "Search algorithm",
        ["BFS", "DFS", "UCS", "A*", "Compare all algorithms"],
    )

    road_labels = [
        f"{a} — {b} ({distance} km)" for a, b, distance in ROADS
    ]
    selected_labels = st.multiselect(
        "Blocked roads (optional)", road_labels
    )
    run_search = st.button(
        "Find route", type="primary", use_container_width=True
    )

blocked_roads = []
for label in selected_labels:
    road_text = label.split(" (")[0]
    city1, city2 = road_text.split(" — ")
    blocked_roads.append((city1, city2))

working_graph = build_graph(blocked_roads)

st.subheader("Road Network")
st.write(
    "Nodes represent cities. Edges represent roads, and edge labels show "
    "approximate distances in kilometres."
)

if run_search:
    if start == goal:
        st.warning("Choose different starting and destination cities.")
        st.stop()

    if algorithm_name == "Compare all algorithms":
        results = compare_algorithms(
            working_graph, start, goal, CITIES
        )
        rows = []
        for name, result in results.items():
            rows.append({
                "Algorithm": name,
                "Route": (
                    " → ".join(result["path"])
                    if result["path"] else "No route"
                ),
                "Distance (km)": result["distance"],
                "Explored nodes": result["explored_count"],
                "Execution time (seconds)": result["execution_time"],
            })

        st.subheader("Algorithm Performance Comparison")
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )

        chosen = results["A*"]
        selected_path = chosen["path"]
        selected_explored = chosen["explored_order"]
        st.write("The map below displays the A* result.")
    else:
        searchers = {
            "BFS": lambda: bfs(working_graph, start, goal),
            "DFS": lambda: dfs(working_graph, start, goal),
            "UCS": lambda: ucs(working_graph, start, goal),
            "A*": lambda: astar(working_graph, start, goal, CITIES),
        }
        selected_path, selected_explored = searchers[algorithm_name]()
        distance = calculate_cost(working_graph, selected_path)

        st.subheader(f"{algorithm_name} Search Result")
        if selected_path:
            c1, c2, c3 = st.columns(3)
            c1.metric("Route distance", f"{distance} km")
            c2.metric("Explored nodes", len(selected_explored))
            c3.metric("Cities in route", len(selected_path))
        else:
            st.error("No route exists with the selected road closures.")

    if selected_path:
        st.success("Route: " + " → ".join(selected_path))

    st.write(
        "Exploration order: "
        + (" → ".join(selected_explored) if selected_explored else "None")
    )

    fig = create_map_figure(
        working_graph,
        route=selected_path,
        explored=selected_explored,
        blocked_roads=blocked_roads,
    )
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
else:
    fig = create_map_figure(
        working_graph, blocked_roads=blocked_roads
    )
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

st.divider()
st.subheader("AI Algorithms Used")

left, right = st.columns(2)
with left:
    st.markdown(
        "**BFS:** explores level by level; minimizes number of edges, "
        "not necessarily weighted distance.\n\n"
        "**DFS:** explores a branch deeply before backtracking; "
        "does not guarantee an optimal route."
    )
with right:
    st.markdown(
        "**UCS:** expands the lowest accumulated path cost.\n\n"
        "**A*:** uses `f(n) = g(n) + h(n)` to combine travelled cost "
        "with an estimate of remaining distance."
    )

st.caption(
    "Academic demonstration only. Road links and distances are illustrative; "
    "there is no live traffic, GPS tracking, or turn-by-turn navigation."
)
