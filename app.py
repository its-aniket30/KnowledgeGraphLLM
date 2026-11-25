
import streamlit as st
import pandas as pd
import networkx as nx

from pathlib import Path

from config.settings import (
    APP_NAME,
    APP_VERSION,
    BASE_DIR,
    RAW_DATA_DIR
)

from core.graph_builder import KnowledgeGraphBuilder
from core.dataset_processor import DatasetProcessor
from core.graph_storage import GraphStorage

from visualization.graph_visualizer import create_network_figure

from algorithms.centrality import CentralityAnalyzer
from algorithms.community_detection import CommunityDetector
from algorithms.path_analysis import PathAnalyzer


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧠",
    layout="wide"
)


# =====================================================
# LOAD GRAPH BUILDER
# =====================================================

@st.cache_resource
def get_graph_builder():
    return KnowledgeGraphBuilder()


builder = get_graph_builder()


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def graph_to_relations(graph):
    """Convert graph edges into a relationship list."""

    relations = []

    for source, target, attributes in graph.edges(data=True):

        relations.append({
            "subject": graph.nodes[source].get("name", source),
            "predicate": attributes.get(
                "predicate",
                attributes.get("relation", "related_to")
            ),
            "object": graph.nodes[target].get("name", target)
        })

    return relations


def create_graph_result(graph):
    """Create a common result structure for all graph sources."""

    return {
        "graph": graph,
        "relations": graph_to_relations(graph),
        "statistics": {
            "nodes": graph.number_of_nodes(),
            "edges": graph.number_of_edges(),
            "density": nx.density(graph) if graph.number_of_nodes() > 1 else 0
        }
    }


# =====================================================
# APPLICATION HEADER
# =====================================================

st.title("🧠 KnowledgeGraphLLM")

st.caption(
    "AI-Powered Knowledge Graph Extraction and Analysis System"
)

st.divider()


# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "Dataset Manager",
        "Text Extraction",
        "Graph Generator",
        "Algorithm Analysis",
        "Reports"
    ]
)


# =====================================================
# DASHBOARD
# =====================================================

if page == "Dashboard":

    st.header("Project Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Version", APP_VERSION)
    col2.metric("Graph Engine", "NetworkX")
    col3.metric("Processing Mode", "Offline-first")

    st.divider()

    st.subheader("System Overview")

    st.success("Streamlit application is running successfully.")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Project Information")

        st.write(f"**Project:** {APP_NAME}")
        st.write(f"**Version:** {APP_VERSION}")
        st.write(f"**Location:** `{BASE_DIR}`")

    with col2:

        st.markdown("### Technology Stack")

        st.write("- Python")
        st.write("- Streamlit")
        st.write("- spaCy")
        st.write("- FastCoref")
        st.write("- NetworkX")
        st.write("- Plotly")


# =====================================================
# DATASET MANAGER
# =====================================================

elif page == "Dataset Manager":

    st.header("Dataset Manager")

    st.write(
        "Upload TXT, CSV or JSON datasets to extract "
        "entities and relationships and generate a combined graph."
    )

    uploaded_file = st.file_uploader(
        "Upload your dataset",
        type=["txt", "csv", "json"],
        help="Supported formats: TXT, CSV and JSON."
    )

    if uploaded_file is not None:

        st.info(
            f"Selected file: **{uploaded_file.name}** "
            f"({uploaded_file.size:,} bytes)"
        )

        if st.button(
            "Process Dataset",
            type="primary"
        ):

            progress_bar = st.progress(0, text="Preparing dataset...")
            status_text = st.empty()

            try:

                # Save uploaded file inside datasets/raw
                safe_filename = Path(uploaded_file.name).name
                file_path = RAW_DATA_DIR / safe_filename

                file_path.write_bytes(uploaded_file.getvalue())

                # Reuse the cached graph builder
                processor = DatasetProcessor(
                    graph_builder=builder
                )

                def update_progress(completed, total):

                    progress = completed / total

                    progress_bar.progress(
                        progress,
                        text=f"Processing record {completed} of {total}"
                    )

                    status_text.write(
                        f"Processed {completed}/{total} records"
                    )

                with st.spinner(
                    "Extracting knowledge from dataset..."
                ):

                    dataset_result = processor.process_dataset(
                        file_path,
                        progress_callback=update_progress
                    )

                graph = dataset_result["graph"]

                # Normalize dataset result for other modules
                graph_result = create_graph_result(graph)

                graph_result["dataset_summary"] = {
                    "total_records": dataset_result["total_records"],
                    "successful_records": dataset_result["successful_records"],
                    "failed_records": dataset_result["failed_records"]
                }

                st.session_state["graph_result"] = graph_result
                st.session_state["dataset_result"] = dataset_result

                progress_bar.progress(
                    1.0,
                    text="Dataset processing completed!"
                )

                status_text.empty()

                if dataset_result["successful_records"] > 0:

                    st.success(
                        "Dataset processed successfully!"
                    )

                else:

                    st.warning(
                        "No records were processed successfully. "
                        "Check the failure details below."
                    )

            except Exception as error:

                progress_bar.empty()

                st.error(
                    f"Dataset processing failed: {error}"
                )

    # -------------------------------------------------
    # DATASET RESULTS
    # -------------------------------------------------

    if "dataset_result" in st.session_state:

        dataset_result = st.session_state["dataset_result"]
        graph = dataset_result["graph"]

        st.divider()

        st.subheader("Dataset Processing Results")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Records",
            dataset_result["total_records"]
        )

        col2.metric(
            "Successful",
            dataset_result["successful_records"]
        )

        col3.metric(
            "Failed",
            len(dataset_result["failed_records"])
        )

        col4.metric(
            "Graph Nodes",
            dataset_result["nodes"]
        )

        col5, col6 = st.columns(2)

        col5.metric(
            "Graph Relationships",
            dataset_result["edges"]
        )

        col6.metric(
            "Processing Success Rate",
            f'{dataset_result["successful_records"] / dataset_result["total_records"] * 100:.1f}%'
            if dataset_result["total_records"] > 0 else "0%"
        )

        # -------------------------------------------------
        # FAILED RECORDS
        # -------------------------------------------------

        if dataset_result["failed_records"]:

            with st.expander("View Failed Records"):

                st.dataframe(
                    pd.DataFrame(dataset_result["failed_records"]),
                    use_container_width=True
                )

        # -------------------------------------------------
        # COMBINED GRAPH
        # -------------------------------------------------

        st.divider()

        st.subheader("Combined Knowledge Graph")

        if graph.number_of_nodes() > 0:

            st.plotly_chart(
                create_network_figure(graph),
                use_container_width=True
            )

            st.subheader("Extracted Relationships")

            st.dataframe(
                pd.DataFrame(
                    graph_to_relations(graph)
                ),
                use_container_width=True
            )

            st.subheader("Export Knowledge Graph")

            storage = GraphStorage()

            col1, col2 = st.columns(2)

            with col1:

                if st.button("Prepare JSON Export"):

                    try:

                        json_path = storage.save_json(
                            graph,
                            "dataset_knowledge_graph.json"
                        )

                        st.session_state["dataset_json_path"] = str(
                            json_path
                        )

                        st.success("JSON export prepared.")

                    except Exception as error:

                        st.error(f"JSON export failed: {error}")

                if "dataset_json_path" in st.session_state:

                    json_path = Path(
                        st.session_state["dataset_json_path"]
                    )

                    if json_path.exists():

                        st.download_button(
                            "Download JSON",
                            data=json_path.read_bytes(),
                            file_name="dataset_knowledge_graph.json",
                            mime="application/json"
                        )

            with col2:

                if st.button("Prepare GraphML Export"):

                    try:

                        graphml_path = storage.save_graphml(
                            graph,
                            "dataset_knowledge_graph.graphml"
                        )

                        st.session_state["dataset_graphml_path"] = str(
                            graphml_path
                        )

                        st.success("GraphML export prepared.")

                    except Exception as error:

                        st.error(f"GraphML export failed: {error}")

                if "dataset_graphml_path" in st.session_state:

                    graphml_path = Path(
                        st.session_state["dataset_graphml_path"]
                    )

                    if graphml_path.exists():

                        st.download_button(
                            "Download GraphML",
                            data=graphml_path.read_bytes(),
                            file_name="dataset_knowledge_graph.graphml",
                            mime="application/graphml+xml"
                        )

        else:

            st.warning(
                "The combined knowledge graph contains no nodes."
            )


# =====================================================
# TEXT EXTRACTION
# =====================================================

elif page == "Text Extraction":

    st.header("Text Extraction")

    input_text = st.text_area(
        "Enter text for knowledge graph extraction",
        height=220,
        placeholder=(
            "Example: Elon Musk founded SpaceX. "
            "SpaceX develops advanced rocket technology."
        )
    )

    if st.button("Extract Knowledge Graph", type="primary"):

        if not input_text.strip():

            st.warning("Please enter some text first.")

        else:

            with st.spinner(
                "Extracting entities and relationships..."
            ):

                try:

                    result = builder.build_graph(input_text)

                    st.session_state["graph_result"] = result

                    # A new text extraction replaces previous dataset results
                    st.session_state.pop("dataset_result", None)
                    st.session_state.pop("dataset_json_path", None)
                    st.session_state.pop("dataset_graphml_path", None)

                    st.success(
                        "Knowledge graph generated successfully!"
                    )

                except Exception as error:

                    st.error(f"Extraction failed: {error}")

    if "graph_result" in st.session_state:

        result = st.session_state["graph_result"]

        st.divider()

        st.subheader("Extraction Results")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Entities",
            result["statistics"]["nodes"]
        )

        col2.metric(
            "Relationships",
            result["statistics"]["edges"]
        )

        col3.metric(
            "Graph Density",
            f'{result["statistics"]["density"]:.3f}'
        )

        st.subheader("Extracted Relationships")

        if result.get("relations"):

            st.dataframe(
                [
                    {
                        "Subject": relation["subject"],
                        "Predicate": relation["predicate"],
                        "Object": relation["object"]
                    }
                    for relation in result["relations"]
                ],
                use_container_width=True
            )

        else:

            st.info("No relationships were detected.")

        st.subheader("Knowledge Graph Visualization")

        figure = create_network_figure(result["graph"])

        st.plotly_chart(
            figure,
            use_container_width=True
        )


# =====================================================
# GRAPH GENERATOR
# =====================================================

elif page == "Graph Generator":

    st.header("Knowledge Graph Generator")

    if "graph_result" in st.session_state:

        graph = st.session_state["graph_result"]["graph"]

        if graph.number_of_nodes() > 0:

            st.plotly_chart(
                create_network_figure(graph),
                use_container_width=True
            )

        else:

            st.warning("The current knowledge graph is empty.")

    else:

        st.info(
            "First generate a graph using Text Extraction "
            "or Dataset Manager."
        )


# =====================================================
# ALGORITHM ANALYSIS
# =====================================================

elif page == "Algorithm Analysis":

    st.header("Knowledge Graph Algorithm Analysis")

    if "graph_result" not in st.session_state:

        st.warning(
            "Please generate a knowledge graph first "
            "using Text Extraction or Dataset Manager."
        )

    else:

        graph = st.session_state["graph_result"]["graph"]

        if graph.number_of_nodes() == 0:

            st.warning("The current knowledge graph is empty.")

        else:

            st.success(
                f"Analyzing graph containing "
                f"{graph.number_of_nodes()} entities and "
                f"{graph.number_of_edges()} relationships."
            )

            tab1, tab2, tab3 = st.tabs(
                [
                    "Centrality Analysis",
                    "Community Detection",
                    "Shortest Path"
                ]
            )

            # -------------------------------------------------
            # TAB 1: CENTRALITY ANALYSIS
            # -------------------------------------------------

            with tab1:

                st.subheader("Centrality Analysis")

                st.write(
                    "Measure the importance and connectivity "
                    "of entities in the knowledge graph."
                )

                try:

                    analyzer = CentralityAnalyzer(graph)

                    centrality_results = analyzer.analyze_all()

                    centrality_data = []

                    for node in graph.nodes:

                        node_data = graph.nodes[node]

                        centrality_data.append({
                            "Entity": node_data.get("name", node),
                            "Entity Type": node_data.get(
                                "entity_type", "UNKNOWN"
                            ),
                            "Degree Centrality": centrality_results[
                                "degree_centrality"
                            ].get(node, 0),

                            "Betweenness Centrality": centrality_results[
                                "betweenness_centrality"
                            ].get(node, 0),

                            "Closeness Centrality": centrality_results[
                                "closeness_centrality"
                            ].get(node, 0),

                            "PageRank": centrality_results[
                                "pagerank"
                            ].get(node, 0)
                        })

                    dataframe = pd.DataFrame(centrality_data)

                    st.dataframe(
                        dataframe.style.format({
                            "Degree Centrality": "{:.4f}",
                            "Betweenness Centrality": "{:.4f}",
                            "Closeness Centrality": "{:.4f}",
                            "PageRank": "{:.4f}"
                        }),
                        use_container_width=True
                    )

                    st.subheader("Entity Importance Ranking")

                    selected_metric = st.selectbox(
                        "Select centrality algorithm",
                        [
                            "Degree Centrality",
                            "Betweenness Centrality",
                            "Closeness Centrality",
                            "PageRank"
                        ]
                    )

                    ranking = dataframe.sort_values(
                        by=selected_metric,
                        ascending=False
                    )

                    st.bar_chart(
                        ranking.set_index("Entity")[
                            selected_metric
                        ]
                    )

                    st.caption(
                        "Higher scores indicate greater centrality "
                        "under the selected measure."
                    )

                except Exception as error:

                    st.error(
                        f"Centrality analysis failed: {error}"
                    )

            # -------------------------------------------------
            # TAB 2: COMMUNITY DETECTION
            # -------------------------------------------------

            with tab2:

                st.subheader("Community Detection")

                st.write(
                    "Discover groups of related entities "
                    "using the Louvain community detection algorithm."
                )

                try:

                    detector = CommunityDetector(graph)

                    communities = detector.get_community_summary()

                    if not communities:

                        st.info("No communities could be detected.")

                    else:

                        st.metric(
                            "Communities Identified",
                            len(communities)
                        )

                        for community_id, details in communities.items():

                            with st.expander(
                                f"Community {community_id} "
                                f"({details['size']} entities)",
                                expanded=True
                            ):

                                for entity in details["entities"]:

                                    node_data = graph.nodes[entity]

                                    st.write(
                                        f"• {node_data.get('name', entity)} "
                                        f"({node_data.get('entity_type', 'UNKNOWN')})"
                                    )

                except Exception as error:

                    st.error(
                        f"Community detection failed: {error}"
                    )

            # -------------------------------------------------
            # TAB 3: SHORTEST PATH ANALYSIS
            # -------------------------------------------------

            with tab3:

                st.subheader("Shortest Path Analysis")

                st.write(
                    "Find how two entities are connected "
                    "through relationships in the knowledge graph."
                )

                entity_options = list(graph.nodes)

                entity_names = {
                    node: graph.nodes[node].get("name", node)
                    for node in entity_options
                }

                source = st.selectbox(
                    "Select source entity",
                    entity_options,
                    format_func=lambda node: entity_names[node],
                    key="path_source"
                )

                target = st.selectbox(
                    "Select target entity",
                    entity_options,
                    format_func=lambda node: entity_names[node],
                    index=min(1, len(entity_options) - 1),
                    key="path_target"
                )

                if st.button("Find Shortest Path", type="primary"):

                    try:

                        path_analyzer = PathAnalyzer(graph)

                        result = path_analyzer.find_shortest_path(
                            source,
                            target
                        )

                        if result["found"]:

                            st.success("Path found successfully!")

                            st.metric(
                                "Path Distance",
                                result["distance"]
                            )

                            st.subheader("Connection Path")

                            path_names = [
                                entity_names[node]
                                for node in result["path"]
                            ]

                            st.code(
                                " → ".join(path_names)
                            )

                            st.write(
                                "**Entities in path:**",
                                len(result["path"])
                            )

                        else:

                            st.warning(result["message"])

                    except Exception as error:

                        st.error(
                            f"Path analysis failed: {error}"
                        )


# =====================================================
# REPORTS
# =====================================================

elif page == "Reports":

    st.header("Reports and Exports")

    if "graph_result" in st.session_state:

        graph = st.session_state["graph_result"]["graph"]

        st.subheader("Current Graph Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric("Entities", graph.number_of_nodes())
        col2.metric("Relationships", graph.number_of_edges())
        col3.metric(
            "Graph Density",
            f'{nx.density(graph):.3f}'
            if graph.number_of_nodes() > 1 else "0.000"
        )

        st.info(
            "Use Dataset Manager to export dataset graphs "
            "as JSON or GraphML."
        )

    else:

        st.info(
            "Generate a graph using Text Extraction or Dataset Manager "
            "to view its report."
        )
