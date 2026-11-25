
import csv
import json
import re
from pathlib import Path

import networkx as nx

from config.settings import BATCH_SIZE, MAX_TEXT_LENGTH
from core.graph_builder import KnowledgeGraphBuilder


class DatasetProcessor:
    """Load datasets and combine extracted knowledge into one graph."""

    def __init__(self, graph_builder=None, batch_size=BATCH_SIZE):
        self.graph_builder = graph_builder or KnowledgeGraphBuilder()
        self.batch_size = max(1, int(batch_size))

    def _read_txt(self, file_path):
        """Read TXT files and split numbered records or paragraphs."""

        text = file_path.read_text(encoding="utf-8-sig")

        if not text.strip():
            return []

        # Split numbered sections such as Record 1:, Record 2:, etc.
        sections = re.split(
            r"(?=^Record\s+\d+\s*:)",
            text,
            flags=re.MULTILINE | re.IGNORECASE
        )

        records = [
            section.strip()
            for section in sections
            if re.match(
                r"^Record\s+\d+\s*:",
                section.strip(),
                flags=re.IGNORECASE
            )
        ]

        if records:
            return records

        # For ordinary TXT files, split on blank lines.
        return [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", text)
            if paragraph.strip()
        ]

    def _read_csv(self, file_path):
        """Read CSV rows as individual text records."""

        records = []

        with file_path.open(
            "r", encoding="utf-8-sig", newline=""
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                text = " ".join(
                    str(value).strip()
                    for value in row.values()
                    if value is not None and str(value).strip()
                )

                if text:
                    records.append(text)

        return records

    def _json_to_text(self, value):
        """Convert nested JSON values into readable text."""

        if value is None:
            return ""

        if isinstance(value, dict):
            parts = []

            for key, item in value.items():
                item_text = self._json_to_text(item)

                if item_text:
                    parts.append(f"{key}: {item_text}")

            return ". ".join(parts)

        if isinstance(value, list):
            return ". ".join(
                text for item in value
                if (text := self._json_to_text(item))
            )

        return str(value).strip()

    def _read_json(self, file_path):
        """Read JSON records, including common dataset containers."""

        with file_path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)

        if isinstance(data, list):
            items = data

        elif isinstance(data, dict):
            items = None

            for key in ("records", "data", "documents", "items"):
                if isinstance(data.get(key), list):
                    items = data[key]
                    break

            items = items if items is not None else [data]

        else:
            items = [data]

        return [
            text for item in items
            if (text := self._json_to_text(item))
        ]

    def load_records(self, file_path):
        """Load text records from TXT, CSV or JSON files."""

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Dataset file not found: {file_path}"
            )

        extension = file_path.suffix.lower()

        if extension == ".txt":
            return self._read_txt(file_path)

        if extension == ".csv":
            return self._read_csv(file_path)

        if extension == ".json":
            return self._read_json(file_path)

        raise ValueError(
            "Unsupported file format. Use TXT, CSV or JSON."
        )

    def _merge_graphs(self, target_graph, source_graph, record_number):
        """Merge one extracted graph into the combined graph."""

        for node, attributes in source_graph.nodes(data=True):

            if node not in target_graph:
                target_graph.add_node(node, **attributes)
                continue

            existing = target_graph.nodes[node]

            existing["frequency"] = (
                existing.get("frequency", 0)
                + attributes.get("frequency", 0)
            )

            labels = set(existing.get("labels", []))
            labels.update(attributes.get("labels", []))
            existing["labels"] = sorted(labels)

            if existing.get("entity_type") == "UNKNOWN":
                existing["entity_type"] = attributes.get(
                    "entity_type", "UNKNOWN"
                )

        for source, target, attributes in source_graph.edges(data=True):
            edge_attributes = dict(attributes)
            edge_attributes["record_number"] = record_number

            target_graph.add_edge(
                source,
                target,
                **edge_attributes
            )

    def process_dataset(self, file_path, progress_callback=None):
        """Process records and return one combined knowledge graph."""

        records = self.load_records(file_path)

        if not records:
            raise ValueError("The dataset contains no readable records.")

        combined_graph = nx.MultiDiGraph()

        successful_records = 0
        failed_records = []
        total_records = len(records)

        for batch_start in range(0, total_records, self.batch_size):

            batch = records[
                batch_start:batch_start + self.batch_size
            ]

            for offset, text in enumerate(batch):
                record_number = batch_start + offset + 1

                try:
                    # Prevent excessively large records from exhausting RAM.
                    if len(text) > MAX_TEXT_LENGTH:
                        raise ValueError(
                            f"Record is too large: {len(text)} characters. "
                            f"Maximum allowed: {MAX_TEXT_LENGTH}."
                        )

                    result = self.graph_builder.build_graph(text)

                    self._merge_graphs(
                        combined_graph,
                        result["graph"],
                        record_number
                    )

                    successful_records += 1

                except Exception as error:
                    failed_records.append({
                        "record_number": record_number,
                        "error": str(error)
                    })

                if progress_callback:
                    progress_callback(
                        record_number,
                        total_records
                    )

        return {
            "graph": combined_graph,
            "total_records": total_records,
            "successful_records": successful_records,
            "failed_records": failed_records,
            "nodes": combined_graph.number_of_nodes(),
            "edges": combined_graph.number_of_edges()
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python -m core.dataset_processor "
            "datasets/samples/sample.txt"
        )
        raise SystemExit(1)

    processor = DatasetProcessor()
    result = processor.process_dataset(sys.argv[1])

    print("\nDataset Processing Results")
    print("--------------------------")
    print("Total records:", result["total_records"])
    print("Successful:", result["successful_records"])
    print("Failed:", len(result["failed_records"]))
    print("Graph nodes:", result["nodes"])
    print("Graph edges:", result["edges"])

    if result["failed_records"]:
        print("\nFailed records:")

        for failure in result["failed_records"]:
            print(failure)
