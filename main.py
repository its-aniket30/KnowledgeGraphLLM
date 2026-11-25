
import os
import json
from pathlib import Path

import networkx as nx
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from openai import OpenAI


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("NVIDIA_API_KEY")
base_url = os.getenv(
    "NVIDIA_BASE_URL",
    "https://integrate.api.nvidia.com/v1"
)
model = os.getenv(
    "NVIDIA_MODEL",
    "nvidia/nemotron-3.5-lightning-30b-a3b"
)

if not api_key or "PASTE_YOUR_REAL_KEY" in api_key:
    raise ValueError(
        "NVIDIA_API_KEY is missing. Check your .env file."
    )

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    timeout=120.0
)


# ==========================================
# 2. EXTRACT TRIPLES USING NVIDIA NEMOTRON
# ==========================================

def extract_triples(text):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract factual subject-relation-object "
                    "triples from the provided text. Return "
                    "valid JSON only, in this format: "
                    '{"triples":[{"subject":"Google",'
                    '"relation":"developed","object":"Gemini",'
                    '"evidence":"Google developed Gemini."}]}. '
                    "Only extract relationships supported by "
                    "the source text. Do not invent facts."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0,
        max_tokens=3000
    )

    content = response.choices[0].message.content or ""
    start = content.find("{")
    end = content.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError(
            "The model did not return valid JSON:\n" + content
        )

    data = json.loads(content[start:end + 1])
    raw_triples = data.get("triples", [])

    if not isinstance(raw_triples, list):
        raise ValueError("'triples' must be a JSON list.")

    valid_triples = []

    for item in raw_triples:
        if not isinstance(item, dict):
            continue

        subject = item.get("subject")
        relation = item.get("relation")
        obj = item.get("object")
        evidence = item.get("evidence", "")

        if not all(
            isinstance(value, str) and value.strip()
            for value in (subject, relation, obj)
        ):
            continue

        valid_triples.append({
            "subject": subject.strip(),
            "relation": relation.strip(),
            "object": obj.strip(),
            "evidence": (
                evidence.strip()
                if isinstance(evidence, str)
                else ""
            )
        })

    return valid_triples


# ==========================================
# 3. BUILD AND SAVE KNOWLEDGE GRAPH
# ==========================================

def build_graph(triples):
    graph = nx.MultiDiGraph()

    for triple in triples:
        graph.add_edge(
            triple["subject"],
            triple["object"],
            relation=triple["relation"],
            evidence=triple["evidence"]
        )

    return graph


# ==========================================
# 4. VISUALIZE KNOWLEDGE GRAPH
# ==========================================

def visualize_graph(graph):
    output_path = BASE_DIR / "knowledge_graph.png"

    if graph.number_of_nodes() == 0:
        print("Graph is empty; no visualization generated.")
        return

    # Combine parallel relationships for clearer labels.
    display_graph = nx.DiGraph()
    display_graph.add_nodes_from(graph.nodes())

    labels = {}

    for source, target, _, data in graph.edges(
        keys=True, data=True
    ):
        labels.setdefault((source, target), [])

        relation = data["relation"]
        if relation not in labels[(source, target)]:
            labels[(source, target)].append(relation)

    for (source, target), relations in labels.items():
        display_graph.add_edge(
            source,
            target,
            label=", ".join(relations)
        )

    fig, ax = plt.subplots(figsize=(12, 8))

    pos = nx.spring_layout(display_graph, seed=42)

    nx.draw_networkx(
        display_graph,
        pos,
        ax=ax,
        node_color="lightblue",
        node_size=2600,
        font_size=9,
        arrows=True,
        arrowsize=20
    )

    nx.draw_networkx_edge_labels(
        display_graph,
        pos,
        ax=ax,
        edge_labels=nx.get_edge_attributes(
            display_graph, "label"
        ),
        font_size=8
    )

    ax.set_title("Knowledge Graph - NVIDIA Nemotron")
    ax.axis("off")
    fig.tight_layout()

    # Save the image before displaying it.
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    print(f"Saved graph image: {output_path}", flush=True)

    # Non-blocking display so the entity query can continue.
    try:
        plt.show(block=False)
        plt.pause(1)
    except Exception as error:
        print(f"Could not display graph window: {error}")

    plt.close(fig)


# ==========================================
# 5. INTERACTIVE ENTITY QUERY
# ==========================================

def query_entity(graph):
    print(
        "\nEnter an entity to query, or type 'exit' to finish.",
        flush=True
    )

    while True:
        try:
            entity = input("\nEntity: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting entity query.")
            break

        if entity.casefold() in {"exit", "quit"}:
            print("Entity query finished.")
            break

        if not entity:
            print("Please enter an entity name.")
            continue

        # Case-insensitive exact matching.
        matched = next(
            (
                node for node in graph.nodes
                if node.casefold() == entity.casefold()
            ),
            None
        )

        if matched is None:
            print(
                f"Entity '{entity}' not found. "
                "Try Google, Gemini, OpenAI, ChatGPT, "
                "Python, or NetworkX."
            )
            continue

        found = False

        # Relationships going out from the entity.
        for _, target, _, data in graph.out_edges(
            matched, keys=True, data=True
        ):
            print(
                f"{matched} --[{data['relation']}]--> {target}"
            )
            found = True

        # Relationships coming into the entity.
        for source, _, _, data in graph.in_edges(
            matched, keys=True, data=True
        ):
            print(
                f"{source} --[{data['relation']}]--> {matched}"
            )
            found = True

        if not found:
            print("No relationships found for this entity.")


# ==========================================
# 6. MAIN PROGRAM
# ==========================================

def main():
    source_file = BASE_DIR / "sample.txt"
    output_file = BASE_DIR / "triples.json"

    if not source_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {source_file}"
        )

    text = source_file.read_text(
        encoding="utf-8"
    ).strip()

    if not text:
        raise ValueError("sample.txt is empty.")

    print("Extracting triples using NVIDIA Nemotron...", flush=True)

    triples = extract_triples(text)

    if not triples:
        print("No triples were extracted.")
        return

    print("\nExtracted triples:")

    for index, triple in enumerate(triples, start=1):
        print(
            f"{index}. ({triple['subject']}, "
            f"{triple['relation']}, {triple['object']})"
        )

    # Save extracted triples.
    output_file.write_text(
        json.dumps(
            triples,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )
    print("\nSaved triples.json")

    # Build graph.
    graph = build_graph(triples)

    print("Entities:", graph.number_of_nodes())
    print("Relationships:", graph.number_of_edges())

    # Generate graph image.
    visualize_graph(graph)

    # Start query independently of graph display.
    query_entity(graph)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\nProject error: {error}")
