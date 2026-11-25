
import networkx as nx

from core.nlp_engine import NLPProcessingEngine
from core.entity_extractor import EntityExtractor
from core.relation_extractor import RelationExtractor
from core.coreference_resolver import CoreferenceResolver


class KnowledgeGraphBuilder:
    """Build a directed knowledge graph using NLP and coreference resolution."""

    def __init__(self):
        # Initialize NLP engine
        self.nlp_engine = NLPProcessingEngine()

        # Initialize coreference resolver
        self.coreference_resolver = CoreferenceResolver(device="cpu")

        # Initialize extractors using the same NLP engine
        self.entity_extractor = EntityExtractor(
            self.nlp_engine
        )

        self.relation_extractor = RelationExtractor(
            self.nlp_engine
        )

        self.graph = nx.MultiDiGraph()

    @staticmethod
    def normalize_name(name):
        """Normalize entity names for graph identification."""
        return " ".join(name.split()).casefold()

    def add_entities(self, entities):
        """Add extracted entities as graph nodes."""

        for entity in entities:
            node_id = entity["normalized"]

            if self.graph.has_node(node_id):
                self.graph.nodes[node_id]["frequency"] += entity["frequency"]

                # Merge entity labels if necessary
                existing_labels = self.graph.nodes[node_id]["labels"]

                self.graph.nodes[node_id]["labels"] = sorted(
                    set(existing_labels + entity["labels"])
                )

                continue

            self.graph.add_node(
                node_id,
                name=entity["name"],
                labels=entity["labels"],
                frequency=entity["frequency"],
                entity_type=entity["labels"][0]
            )

    def add_relations(self, relations):
        """Add extracted relationships as directed edges."""

        for relation in relations:
            subject = self.normalize_name(relation["subject"])
            obj = self.normalize_name(relation["object"])

            # Add missing subject node
            if not self.graph.has_node(subject):
                self.graph.add_node(
                    subject,
                    name=relation["subject"],
                    labels=["UNKNOWN"],
                    entity_type="UNKNOWN",
                    frequency=1
                )

            # Add missing object node
            if not self.graph.has_node(obj):
                self.graph.add_node(
                    obj,
                    name=relation["object"],
                    labels=["UNKNOWN"],
                    entity_type="UNKNOWN",
                    frequency=1
                )

            self.graph.add_edge(
                subject,
                obj,
                relation=relation["predicate"],
                predicate=relation["predicate"]
            )

    def build_graph(self, text):
        """Resolve references, extract knowledge and build the graph."""

        if not isinstance(text, str) or not text.strip():
            raise ValueError("Input text cannot be empty.")

        # Reset graph for each new document
        self.graph = nx.MultiDiGraph()

        # Step 1: Resolve coreferences
        coreference_result = self.coreference_resolver.resolve(text)

        resolved_text = coreference_result["resolved_text"]

        # Step 2: Extract entities from resolved text
        entity_result = self.entity_extractor.extract_and_summarize(
            resolved_text
        )

        # Step 3: Extract relationships from resolved text
        relations = self.relation_extractor.extract_relations(
            resolved_text
        )

        # Step 4: Add entities and relationships to graph
        self.add_entities(entity_result["unique_entities"])
        self.add_relations(relations)

        # Step 5: Calculate coreference statistics
        resolved_mentions = sum(
            1
            for cluster in coreference_result["clusters"]
            for mention in cluster["mentions"]
            if not mention["canonical"]
        )

        coreference_statistics = {
            "total_clusters": coreference_result["total_clusters"],
            "resolved_mentions": resolved_mentions
        }

        return {
            "original_text": text,
            "resolved_text": resolved_text,
            "coreference": coreference_result,
            "coreference_statistics": coreference_statistics,
            "entities": entity_result,
            "relations": relations,
            "graph": self.graph,
            "statistics": self.get_statistics()
        }

    def get_statistics(self):
        """Calculate basic graph statistics."""

        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "is_directed": self.graph.is_directed(),
            "is_multigraph": self.graph.is_multigraph(),
            "density": nx.density(self.graph)
        }

    def export_graph_data(self):
        """Convert graph into JSON-compatible node and edge lists."""

        nodes = []

        for node_id, attributes in self.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                **attributes
            })

        edges = []

        for source, target, key, attributes in self.graph.edges(
            keys=True,
            data=True
        ):
            edges.append({
                "source": source,
                "target": target,
                "key": key,
                **attributes
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "statistics": self.get_statistics()
        }


if __name__ == "__main__":

    builder = KnowledgeGraphBuilder()

    sample_text = (
        "Elon Musk founded SpaceX. "
        "Elon Musk is an entrepreneur. "
        "He also leads Tesla. "
        "Tesla develops electric cars. "
        "The company operates in the automotive industry."
    )

    result = builder.build_graph(sample_text)

    print("\n========== ORIGINAL TEXT ==========")
    print(result["original_text"])

    print("\n========== RESOLVED TEXT ==========")
    print(result["resolved_text"])

    print("\n========== COREFERENCE STATISTICS ==========")
    print(result["coreference_statistics"])

    print("\n========== EXTRACTED ENTITIES ==========")

    for entity in result["entities"]["unique_entities"]:
        print(
            entity["name"],
            "| Frequency:",
            entity["frequency"],
            "| Labels:",
            entity["labels"]
        )

    print("\n========== EXTRACTED RELATIONSHIPS ==========")

    for relation in result["relations"]:
        print(
            relation["subject"],
            "->",
            relation["predicate"],
            "->",
            relation["object"]
        )

    print("\n========== KNOWLEDGE GRAPH STATISTICS ==========")
    print(result["statistics"])

    print("\n========== GRAPH NODES ==========")

    for node, attributes in result["graph"].nodes(data=True):
        print(node, attributes)

    print("\n========== GRAPH EDGES ==========")

    for source, target, attributes in result["graph"].edges(data=True):
        print(source, "->", target, attributes)

    print("\n========== EXPORTED GRAPH DATA ==========")
    print(builder.export_graph_data())
