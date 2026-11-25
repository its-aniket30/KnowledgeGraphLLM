
import networkx as nx


class PathAnalyzer:
    """Find paths and connections between knowledge graph entities."""

    def __init__(self, graph):
        if not isinstance(graph, nx.Graph):
            raise TypeError("Input must be a NetworkX graph.")

        self.graph = graph

    def find_shortest_path(self, source, target):
        if source not in self.graph:
            return {
                "found": False,
                "message": f"Source entity '{source}' not found."
            }

        if target not in self.graph:
            return {
                "found": False,
                "message": f"Target entity '{target}' not found."
            }

        try:
            path = nx.shortest_path(
                self.graph,
                source=source,
                target=target
            )

            return {
                "found": True,
                "path": path,
                "distance": len(path) - 1
            }

        except nx.NetworkXNoPath:
            return {
                "found": False,
                "message": "No path exists between these entities."
            }

    def get_all_shortest_paths(self, source, target):
        if source not in self.graph or target not in self.graph:
            return []

        try:
            return list(
                nx.all_shortest_paths(
                    self.graph,
                    source=source,
                    target=target
                )
            )

        except nx.NetworkXNoPath:
            return []


if __name__ == "__main__":

    graph = nx.DiGraph()

    graph.add_edges_from([
        ("Elon Musk", "SpaceX"),
        ("Elon Musk", "Tesla"),
        ("Tesla", "Electric Cars"),
        ("SpaceX", "Rocket Technology"),
        ("Tesla", "Battery Technology"),
        ("Battery Technology", "Electric Cars")
    ])

    analyzer = PathAnalyzer(graph)

    source = "Elon Musk"
    target = "Electric Cars"

    result = analyzer.find_shortest_path(source, target)

    print("\n========== SHORTEST PATH ANALYSIS ==========")

    if result["found"]:
        print("Source:", source)
        print("Target:", target)
        print("Path:", " -> ".join(result["path"]))
        print("Distance:", result["distance"])
    else:
        print(result["message"])

    print("\n========== ALL SHORTEST PATHS ==========")

    paths = analyzer.get_all_shortest_paths(source, target)

    for path in paths:
        print(" -> ".join(path))
