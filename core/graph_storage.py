
import json
from pathlib import Path

import networkx as nx

from config.settings import EXPORT_DIR


class GraphStorage:
    """Save and load knowledge graphs in JSON and GraphML formats."""

    def __init__(self, export_dir=EXPORT_DIR):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def save_json(self, graph, filename="knowledge_graph.json"):
        """Save a MultiDiGraph as JSON."""

        if not isinstance(graph, nx.MultiDiGraph):
            raise TypeError("Expected a NetworkX MultiDiGraph.")

        data = {
            "directed": True,
            "multigraph": True,
            "nodes": [
                {"id": node, **attributes}
                for node, attributes in graph.nodes(data=True)
            ],
            "edges": [
                {
                    "source": source,
                    "target": target,
                    "key": key,
                    **attributes
                }
                for source, target, key, attributes
                in graph.edges(keys=True, data=True)
            ]
        }

        output_path = self.export_dir / filename

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        return output_path

    def load_json(self, filename="knowledge_graph.json"):
        """Load a previously saved knowledge graph."""

        input_path = self.export_dir / filename

        if not input_path.exists():
            raise FileNotFoundError(
                f"Graph file not found: {input_path}"
            )

        with input_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        graph = nx.MultiDiGraph()

        for node in data["nodes"]:
            attributes = node.copy()
            node_id = attributes.pop("id")
            graph.add_node(node_id, **attributes)

        for edge in data["edges"]:
            attributes = edge.copy()

            source = attributes.pop("source")
            target = attributes.pop("target")
            key = attributes.pop("key", None)

            graph.add_edge(
                source,
                target,
                key=key,
                **attributes
            )

        return graph

    def save_graphml(self, graph, filename="knowledge_graph.graphml"):
        """Save a graph in GraphML format."""

        if not isinstance(graph, nx.MultiDiGraph):
            raise TypeError("Expected a NetworkX MultiDiGraph.")

        # GraphML does not directly support Python lists.
        # Convert list attributes into comma-separated strings.
        graph_copy = graph.copy()

        for _, attributes in graph_copy.nodes(data=True):
            for key, value in list(attributes.items()):
                if isinstance(value, (list, tuple)):
                    attributes[key] = ", ".join(map(str, value))

        for _, _, _, attributes in graph_copy.edges(
            keys=True, data=True
        ):
            for key, value in list(attributes.items()):
                if isinstance(value, (list, tuple)):
                    attributes[key] = ", ".join(map(str, value))

        output_path = self.export_dir / filename

        nx.write_graphml(graph_copy, output_path)

        return output_path


if __name__ == "__main__":
    from core.graph_builder import KnowledgeGraphBuilder

    sample_text = (
        "Elon Musk founded SpaceX in the United States. "
        "SpaceX develops advanced rocket technology. "
        "Elon Musk leads Tesla."
    )

    builder = KnowledgeGraphBuilder()
    result = builder.build_graph(sample_text)

    storage = GraphStorage()

    # Save JSON
    json_path = storage.save_json(result["graph"])
    print("\nJSON saved:", json_path)

    # Load JSON
    loaded_graph = storage.load_json()
    print("JSON loaded successfully.")

    # Save GraphML
    graphml_path = storage.save_graphml(result["graph"])
    print("GraphML saved:", graphml_path)

    # Verify graph
    print("\nOriginal nodes:", result["graph"].number_of_nodes())
    print("Loaded nodes:", loaded_graph.number_of_nodes())

    print("Original edges:", result["graph"].number_of_edges())
    print("Loaded edges:", loaded_graph.number_of_edges())

    assert (
        result["graph"].number_of_nodes()
        == loaded_graph.number_of_nodes()
    )

    assert (
        result["graph"].number_of_edges()
        == loaded_graph.number_of_edges()
    )

    print("\nGraph storage test passed successfully!")
