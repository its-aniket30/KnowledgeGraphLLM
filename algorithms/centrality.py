
import networkx as nx


class CentralityAnalyzer:
    """Calculate centrality measures for a knowledge graph."""

    def __init__(self, graph):
        self.graph = graph

        if not isinstance(graph, nx.Graph):
            raise TypeError("Input must be a NetworkX graph.")

    def calculate_degree_centrality(self):
        return nx.degree_centrality(self.graph)

    def calculate_betweenness_centrality(self):
        return nx.betweenness_centrality(self.graph)

    def calculate_closeness_centrality(self):
        return nx.closeness_centrality(self.graph)

    def calculate_pagerank(self):
        if self.graph.number_of_nodes() == 0:
            return {}

        return nx.pagerank(self.graph)

    def analyze_all(self):
        return {
            "degree_centrality": self.calculate_degree_centrality(),
            "betweenness_centrality": self.calculate_betweenness_centrality(),
            "closeness_centrality": self.calculate_closeness_centrality(),
            "pagerank": self.calculate_pagerank()
        }


if __name__ == "__main__":
    graph = nx.DiGraph()

    graph.add_edges_from([
        ("Elon Musk", "SpaceX"),
        ("Elon Musk", "Tesla"),
        ("Tesla", "Electric Cars"),
        ("SpaceX", "Rocket Technology")
    ])

    analyzer = CentralityAnalyzer(graph)
    results = analyzer.analyze_all()

    for algorithm, scores in results.items():
        print(f"\n========== {algorithm.upper()} ==========")

        for entity, score in sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True
        ):
            print(f"{entity}: {score:.4f}")
