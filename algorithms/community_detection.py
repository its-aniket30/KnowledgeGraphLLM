
import networkx as nx
import community as community_louvain


class CommunityDetector:
    """Detect communities in a knowledge graph."""

    def __init__(self, graph):
        if not isinstance(graph, nx.Graph):
            raise TypeError("Input must be a NetworkX graph.")

        self.graph = graph

    def detect_communities(self):
        if self.graph.number_of_nodes() == 0:
            return {}

        # Louvain works on an undirected graph.
        undirected_graph = nx.Graph(self.graph)

        if undirected_graph.number_of_edges() == 0:
            return {
                node: index
                for index, node in enumerate(undirected_graph.nodes())
            }

        return community_louvain.best_partition(
            undirected_graph,
            weight="weight",
            random_state=42
        )

    def get_community_summary(self):
        partition = self.detect_communities()

        communities = {}

        for node, community_id in partition.items():
            communities.setdefault(community_id, []).append(node)

        return {
            community_id: {
                "community_id": community_id,
                "size": len(nodes),
                "entities": nodes
            }
            for community_id, nodes in communities.items()
        }


if __name__ == "__main__":

    graph = nx.Graph()

    graph.add_edges_from([
        ("Elon Musk", "SpaceX"),
        ("Elon Musk", "Tesla"),
        ("Tesla", "Electric Cars"),
        ("SpaceX", "Rocket Technology"),
        ("Google", "DeepMind"),
        ("Google", "Gemini"),
        ("DeepMind", "Artificial Intelligence"),
        ("Microsoft", "OpenAI"),
        ("Microsoft", "Azure"),
        ("OpenAI", "Artificial Intelligence")
    ])

    detector = CommunityDetector(graph)

    results = detector.get_community_summary()

    print("\n========== COMMUNITY DETECTION ==========")

    for community_id, details in results.items():
        print(f"\nCommunity {community_id}")
        print("Size:", details["size"])
        print("Entities:", ", ".join(details["entities"]))
