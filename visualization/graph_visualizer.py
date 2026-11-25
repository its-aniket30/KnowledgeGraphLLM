
import networkx as nx
import plotly.graph_objects as go


# Colors used for different entity types
ENTITY_COLORS = {
    "PERSON": "#4C78A8",
    "ORG": "#F58518",
    "GPE": "#54A24B",
    "LOC": "#54A24B",
    "DATE": "#B279A2",
    "PRODUCT": "#E45756",
    "EVENT": "#72B7B2",
    "UNKNOWN": "#9D9DA1"
}


def create_network_figure(graph):
    """
    Create an interactive Plotly visualization
    from a NetworkX knowledge graph.
    """

    # Handle empty graph
    if graph is None or graph.number_of_nodes() == 0:
        fig = go.Figure()
        fig.update_layout(
            title="No graph data available",
            template="plotly_white"
        )
        return fig

    # Calculate node positions
    positions = nx.spring_layout(
        graph,
        seed=42,
        k=0.9
    )

    # Prepare edge coordinates
    edge_x = []
    edge_y = []
    annotations = []

    for source, target, attributes in graph.edges(data=True):

        x0, y0 = positions[source]
        x1, y1 = positions[target]

        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

        # Add directional arrow
        annotations.append({
            "x": x1,
            "y": y1,
            "ax": x0,
            "ay": y0,
            "xref": "x",
            "yref": "y",
            "axref": "x",
            "ayref": "y",
            "showarrow": True,
            "arrowhead": 3,
            "arrowsize": 1,
            "arrowwidth": 1.2,
            "arrowcolor": "#888888"
        })

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        hoverinfo="none",
        line=dict(
            width=1.3,
            color="#888888"
        )
    )

    # Prepare node information
    node_x = []
    node_y = []
    node_text = []
    node_hover = []
    node_colors = []
    node_sizes = []

    for node_id, attributes in graph.nodes(data=True):

        x, y = positions[node_id]

        name = attributes.get("name", str(node_id))
        labels = attributes.get("labels", [])

        entity_type = attributes.get(
            "entity_type",
            labels[0] if labels else "UNKNOWN"
        )

        frequency = attributes.get("frequency", 1)

        color = ENTITY_COLORS.get(
            entity_type,
            ENTITY_COLORS["UNKNOWN"]
        )

        node_x.append(x)
        node_y.append(y)
        node_text.append(name)
        node_colors.append(color)

        # Make frequently mentioned entities slightly larger
        node_sizes.append(
            min(20 + frequency * 4, 40)
        )

        node_hover.append(
            f"<b>{name}</b><br>"
            f"Type: {entity_type}<br>"
            f"Frequency: {frequency}<br>"
            f"Node ID: {node_id}"
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="top center",
        hovertext=node_hover,
        hoverinfo="text",
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(
                width=1.5,
                color="white"
            )
        )
    )

    # Create figure
    fig = go.Figure(
        data=[
            edge_trace,
            node_trace
        ]
    )

    fig.update_layout(
        title="Interactive Knowledge Graph",
        template="plotly_white",
        showlegend=False,
        hovermode="closest",
        margin=dict(
            b=20,
            l=5,
            r=5,
            t=50
        ),
        annotations=annotations,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        height=650
    )

    return fig


if __name__ == "__main__":

    # Create a sample graph for testing
    graph = nx.MultiDiGraph()

    graph.add_node(
        "elon musk",
        name="Elon Musk",
        labels=["PERSON"],
        entity_type="PERSON",
        frequency=2
    )

    graph.add_node(
        "spacex",
        name="SpaceX",
        labels=["ORG"],
        entity_type="ORG",
        frequency=2
    )

    graph.add_node(
        "tesla",
        name="Tesla",
        labels=["ORG"],
        entity_type="ORG",
        frequency=1
    )

    graph.add_edge(
        "elon musk",
        "spacex",
        predicate="founded"
    )

    graph.add_edge(
        "elon musk",
        "tesla",
        predicate="leads"
    )

    figure = create_network_figure(graph)

    figure.show()
