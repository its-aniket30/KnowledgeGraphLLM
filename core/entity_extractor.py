
import re
from collections import defaultdict

from core.nlp_engine import NLPProcessingEngine


class EntityExtractor:
    """Extract and organize named entities using local spaCy NLP."""

    ORGANIZATION_NAMES = {
        "spacex",
        "tesla",
        "neuralink",
        "openai",
        "google",
        "microsoft",
        "apple",
        "amazon",
        "meta",
        "nasa",
        "isro",
        "ibm",
        "infosys",
        "tcs",
        "wipro",
        "accenture"
    }

    def __init__(self, nlp_engine=None):
        self.nlp_engine = nlp_engine or NLPProcessingEngine()

    @staticmethod
    def clean_entity_name(name):
        """Clean surrounding whitespace and punctuation."""

        return re.sub(
            r"^[^\w]+|[^\w]+$",
            "",
            name.strip()
        ).strip()

    @staticmethod
    def normalize_entity_name(name):
        """Generate a normalized entity identifier."""

        return " ".join(name.split()).casefold()

    def correct_entity_label(self, entity_text, label):
        """
        Apply controlled organization-name correction.

        Existing spaCy labels are preserved unless a known
        organization has been assigned a different label.
        """

        normalized = self.normalize_entity_name(entity_text)

        if normalized in self.ORGANIZATION_NAMES:
            return "ORG"

        return label

    def extract_entities(self, text):
        """Extract entity mentions with positions and labels."""

        doc = self.nlp_engine.process_text(text)

        entities = []

        for ent in doc.ents:

            entity_text = self.clean_entity_name(ent.text)

            if not entity_text:
                continue

            label = self.correct_entity_label(
                entity_text,
                ent.label_
            )

            # Adjust positions if surrounding punctuation was removed.
            leading = len(ent.text) - len(ent.text.lstrip())
            start = ent.start_char + leading
            end = start + len(entity_text)

            entities.append({
                "text": entity_text,
                "label": label,
                "start": start,
                "end": end,
                "normalized": self.normalize_entity_name(
                    entity_text
                )
            })

        return entities

    def get_unique_entities(self, entities):
        """Group repeated mentions of the same entity."""

        grouped = defaultdict(list)

        for entity in entities:

            key = entity["normalized"]

            grouped[key].append({
                "text": entity["text"],
                "label": entity["label"],
                "start": entity["start"],
                "end": entity["end"]
            })

        unique_entities = []

        for normalized_name, mentions in grouped.items():

            labels = sorted({
                mention["label"]
                for mention in mentions
            })

            # Prefer a known, corrected entity label.
            entity_type = (
                "ORG"
                if normalized_name in self.ORGANIZATION_NAMES
                else labels[0]
            )

            unique_entities.append({
                "name": mentions[0]["text"],
                "normalized": normalized_name,
                "labels": labels,
                "entity_type": entity_type,
                "frequency": len(mentions),
                "mentions": mentions
            })

        return unique_entities

    def extract_and_summarize(self, text):
        """Extract mentions and generate unique entity summaries."""

        entities = self.extract_entities(text)

        unique_entities = self.get_unique_entities(entities)

        return {
            "total_mentions": len(entities),
            "unique_entity_count": len(unique_entities),
            "entities": entities,
            "unique_entities": unique_entities
        }


if __name__ == "__main__":

    extractor = EntityExtractor()

    sample_text = (
        "Elon Musk founded SpaceX. "
        "SpaceX develops rocket technology in the United States. "
        "Elon Musk also leads Tesla. "
        "Tesla collaborates with OpenAI."
    )

    result = extractor.extract_and_summarize(sample_text)

    print("\n========== ENTITY EXTRACTION ==========")

    print("\nTotal entity mentions:", result["total_mentions"])
    print("Unique entities:", result["unique_entity_count"])

    print("\nExtracted Entities:")

    for entity in result["entities"]:
        print(
            f"Name: {entity['text']} | "
            f"Type: {entity['label']} | "
            f"Position: {entity['start']}-{entity['end']}"
        )

    print("\nUnique Entities:")

    for entity in result["unique_entities"]:
        print(
            f"Name: {entity['name']} | "
            f"Types: {entity['labels']} | "
            f"Entity Type: {entity['entity_type']} | "
            f"Frequency: {entity['frequency']}"
        )
