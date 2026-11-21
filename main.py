"""Intelligent Route Planning System."""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from map_data import CITIES, ROADS, build_graph, create_map_figure
from analysis import compare_algorithms


st.set_page_config(
    page_title="Intelligent Route Planner",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Intelligent Route Planning System")

st.caption(
    "Automatic comparison of BFS, DFS, UCS and A* "
    "for route planning."
)

# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.header("Route Settings")

    city_names = list(CITIES)

    start = st.selectbox(
        "Starting City",
        city_names,
        index=0
    )

    goal = st.selectbox(
        "Destination City",
        city_names,
        index=3
    )

    road_labels = [
        f"{a} — {b} ({distance} km)"
        for a, b, distance in ROADS
    ]

    selected_labels = st.multiselect(
        "Blocked Roads (Optional)",
        road_labels
    )

    run_search = st.button(
        "Find Best Route",
        type="primary",
        use_container_width=True
    )


# ---------------- GRAPH ----------------

blocked_roads = []

for label in selected_labels:

    road_text = label.split(" (")[0]

    city1, city2 = road_text.split(" — ")

    blocked_roads.append((city1, city2))


working_graph = build_graph(blocked_roads)


# ---------------- ROAD NETWORK ----------------

st.subheader("Road Network")

st.write(
    "Select your starting city and destination. "
    "All four search algorithms will run automatically."
)


# ---------------- SEARCH ----------------

if run_search:

    if start == goal:

        st.warning(
            "Starting city and destination must be different."
        )

        st.stop()

    with st.spinner("Running all four search algorithms..."):

        results = compare_algorithms(
            working_graph,
            start,
            goal,
            CITIES
        )

    # ---------------- COMPARISON TABLE ----------------

    st.divider()

    st.subheader("Algorithm Performance Comparison")

    rows = []

    for name, result in results.items():

        rows.append({

            "Algorithm": name,

            "Route": (
                " → ".join(result["path"])
                if result["path"]
                else "No route"
            ),

            "Distance (km)": (
                result["distance"]
            ),

            "Explored Nodes": (
                result["explored_count"]
            ),

            "Execution Time (ms)": (
                round(result["execution_time_ms"], 4)
            ),

            "Cities in Route": (
                result["cities_in_route"]
            ),

            "Status": result["status"]

        })

    comparison_df = pd.DataFrame(rows)

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )

    # ---------------- PERFORMANCE HIGHLIGHTS ----------------

    successful = {
        name: result
        for name, result in results.items()
        if result["path"]
    }

    if not successful:

        st.error(
            "No route exists between the selected cities "
            "with the current road closures."
        )

        st.stop()

    st.subheader("Performance Highlights")

    fastest_name = min(
        successful,
        key=lambda name: successful[name]["execution_time"]
    )

    fewest_explored_name = min(
        successful,
        key=lambda name: successful[name]["explored_count"]
    )

    shortest_distance = min(
        result["distance"]
        for result in successful.values()
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Fastest Algorithm",
        fastest_name,
        f"{successful[fastest_name]['execution_time_ms']:.4f} ms"
    )

    c2.metric(
        "Fewest Nodes Explored",
        fewest_explored_name,
        f"{successful[fewest_explored_name]['explored_count']} nodes"
    )

    c3.metric(
        "Shortest Distance",
        f"{shortest_distance} km"
    )

    # ---------------- RECOMMENDED ROUTE ----------------

    st.divider()

    st.subheader("Recommended Route")

    # UCS guarantees minimum path cost for non-negative
    # edge weights. A* also finds an optimal route here.

    recommended = results["UCS"]

    if not recommended["path"]:

        recommended = results["A*"]

    selected_path = recommended["path"]

    selected_explored = recommended["explored_order"]

    st.success(
        f"Recommended route: {' → '.join(selected_path)}"
    )

    st.write(
        f"**Total Distance:** {recommended['distance']} km"
    )

    st.write(
        f"**Algorithm used for recommended route:** "
        f"{'UCS' if recommended['path'] == results['UCS']['path'] else 'A*'}"
    )

    # ---------------- EXPLORATION DETAILS ----------------

    st.subheader("Search Exploration Details")

    for name, result in results.items():

        with st.expander(f"{name} - Exploration Order"):

            st.write(
                " → ".join(result["explored_order"])
            )

            st.write(
                f"Total explored nodes: "
                f"{result['explored_count']}"
            )

    # ---------------- MAP ----------------

    st.divider()

    st.subheader("Route Visualization")

    fig = create_map_figure(
        working_graph,
        route=selected_path,
        explored=selected_explored,
        blocked_roads=blocked_roads
    )

    st.pyplot(fig, use_container_width=True)

    plt.close(fig)


# ---------------- ALGORITHM INFORMATION ----------------

st.divider()

st.subheader("Search Algorithms")

left, right = st.columns(2)

with left:

    st.markdown(
        """
        **1. Breadth-First Search (BFS)**

        Explores nodes level by level.
        Finds a route with the fewest edges.

        **2. Depth-First Search (DFS)**

        Explores one branch deeply before backtracking.
        Does not guarantee the shortest route.
        """
    )

with right:

    st.markdown(
        """
        **3. Uniform Cost Search (UCS)**

        Expands the node with the lowest accumulated
        path cost. Guarantees an optimal route.

        **4. A* Search**

        Uses:

        `f(n) = g(n) + h(n)`

        Combines the travelled cost and estimated
        remaining distance.
        """
    )


st.caption(
    "Academic demonstration only. Road connections and "
    "distances are illustrative, not live navigation data."
)