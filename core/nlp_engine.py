
import re

import spacy
from spacy.language import Language

from config.settings import SPACY_MODEL


class NLPProcessingEngine:
    """Loads and manages the local spaCy NLP model."""

    ORGANIZATION_PATTERNS = [
        "SpaceX",
        "Tesla",
        "Neuralink",
        "OpenAI",
        "Google",
        "Microsoft",
        "Apple",
        "Amazon",
        "Meta",
        "NASA",
        "ISRO",
        "IBM",
        "Infosys",
        "TCS",
        "Wipro",
        "Accenture",
        "NVIDIA",
        "Intel",
        "AMD",
        "Samsung",
        "Oracle",
        "Adobe",
        "Netflix",
        "Uber",
        "Airbnb",
        "PayPal",
        "Qualcomm",
        "Capgemini",
        "Tata Motors",
        "Reliance Industries",
        "Flipkart"
    ]

    def __init__(self, model_name=SPACY_MODEL):
        self.model_name = model_name
        self.nlp: Language | None = None
        self.load_model()

    def load_model(self):
        """Load spaCy and configure custom entity recognition."""

        try:
            self.nlp = spacy.load(self.model_name)

            if "custom_entity_ruler" not in self.nlp.pipe_names:

                ruler = self.nlp.add_pipe(
                    "entity_ruler",
                    name="custom_entity_ruler",
                    after="ner",
                    config={"overwrite_ents": True}
                )

                patterns = []

                for organization in self.ORGANIZATION_PATTERNS:

                    tokens = self.nlp.make_doc(organization)

                    token_pattern = []

                    for index, token in enumerate(tokens):

                        if index == len(tokens) - 1:
                            token_pattern.append({
                                "LOWER": {
                                    "REGEX": (
                                        "^"
                                        + re.escape(token.lower_)
                                        + r"[.,!?;:]*$"
                                    )
                                }
                            })
                        else:
                            token_pattern.append({
                                "LOWER": token.lower_
                            })

                    patterns.append({
                        "label": "ORG",
                        "pattern": token_pattern
                    })

                ruler.add_patterns(patterns)

            print(
                f"Successfully loaded NLP model: {self.model_name}"
            )
            print("Custom entity recognition rules loaded.")

        except OSError as error:
            raise RuntimeError(
                f"spaCy model '{self.model_name}' is not installed. "
                "Install it using: python -m spacy download "
                f"{self.model_name}"
            ) from error

    def process_text(self, text):
        """Process input text and return a spaCy document."""

        if not isinstance(text, str):
            raise TypeError("Input must be a string.")

        text = text.strip()

        if not text:
            raise ValueError("Input text cannot be empty.")

        return self.nlp(text)

    def get_model_info(self):
        """Return information about the loaded NLP model."""

        if self.nlp is None:
            return {"loaded": False}

        return {
            "loaded": True,
            "model_name": self.model_name,
            "pipeline": self.nlp.pipe_names,
            "language": self.nlp.lang
        }


if __name__ == "__main__":

    engine = NLPProcessingEngine()

    sample_text = (
        "Elon Musk founded SpaceX. "
        "SpaceX develops advanced rocket technology. "
        "Elon Musk leads Tesla. "
        "OpenAI develops artificial intelligence. "
        "NVIDIA develops GPUs. "
        "Microsoft works with OpenAI."
    )

    doc = engine.process_text(sample_text)

    print("\n========== DETECTED ENTITIES ==========")

    for entity in doc.ents:
        print(
            f"Entity: {entity.text} | "
            f"Type: {entity.label_}"
        )

    print("\n========== MODEL INFORMATION ==========")
    print(engine.get_model_info())
