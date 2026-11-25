
from fastcoref import FCoref


class CoreferenceResolver:
    """
    Resolve pronouns and repeated references using FastCoref.

    Example:
        Elon Musk founded SpaceX.
        He also leads Tesla.

    Resolved:
        Elon Musk founded SpaceX.
        Elon Musk also leads Tesla.
    """

    def __init__(self, device="cpu"):
        self.device = device
        self.model = None

    def load_model(self):
        """Load the pretrained coreference model once."""

        if self.model is None:
            print("Loading FastCoref model...")

            self.model = FCoref(device=self.device)

            print("FastCoref model loaded successfully.")

    def resolve(self, text):
        """Find coreference clusters and create resolved text."""

        if not isinstance(text, str):
            raise TypeError("Input must be a string.")

        text = text.strip()

        if not text:
            raise ValueError("Input text cannot be empty.")

        self.load_model()

        predictions = self.model.predict(
            texts=[text]
        )

        clusters = predictions[0].get_clusters(
            as_strings=False
        )

        resolved_clusters = []
        replacements = []

        for cluster in clusters:

            if not cluster:
                continue

            # The first mention is used as the canonical mention.
            canonical_start, canonical_end = cluster[0]

            canonical_text = text[
                canonical_start:canonical_end
            ]

            mentions = []

            for start, end in cluster:

                mention_text = text[start:end]

                mentions.append({
                    "text": mention_text,
                    "start": start,
                    "end": end,
                    "canonical": (
                        start == canonical_start
                        and end == canonical_end
                    )
                })

                if start == canonical_start and end == canonical_end:
                    continue

                replacements.append({
                    "start": start,
                    "end": end,
                    "replacement": canonical_text
                })

            resolved_clusters.append({
                "canonical": canonical_text,
                "mentions": mentions
            })

        # Replace from right to left to preserve original offsets.
        resolved_text = text

        for item in sorted(
            replacements,
            key=lambda value: value["start"],
            reverse=True
        ):

            resolved_text = (
                resolved_text[:item["start"]]
                + item["replacement"]
                + resolved_text[item["end"]:]
            )

        return {
            "original_text": text,
            "resolved_text": resolved_text,
            "clusters": resolved_clusters,
            "total_clusters": len(resolved_clusters)
        }


if __name__ == "__main__":

    resolver = CoreferenceResolver(device="cpu")

    sample_text = (
    "Elon Musk founded SpaceX. "
    "Elon Musk is an entrepreneur. "
    "He also leads Tesla. "
    "Tesla develops electric cars. "
    "The company operates in the automotive industry."
)

    result = resolver.resolve(sample_text)

    print("\n========== COREFERENCE RESOLUTION ==========")

    print("\nOriginal Text:")
    print(result["original_text"])

    print("\nResolved Text:")
    print(result["resolved_text"])

    print("\nCoreference Clusters:")

    for cluster in result["clusters"]:

        print("\nCanonical Entity:", cluster["canonical"])

        for mention in cluster["mentions"]:
            print(
                "Mention:",
                mention["text"],
                "| Canonical:",
                mention["canonical"]
            )

    print("\nTotal Clusters:", result["total_clusters"])
