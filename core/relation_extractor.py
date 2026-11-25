
from core.nlp_engine import NLPProcessingEngine


class RelationExtractor:
    """Extract subject-predicate-object relationships from text."""

    def __init__(self, nlp_engine=None):
        self.nlp_engine = nlp_engine or NLPProcessingEngine()

    @staticmethod
    def clean_span(span):
        """Remove surrounding whitespace and trailing punctuation."""

        phrase = span.text

        leading = len(phrase) - len(phrase.lstrip())
        cleaned = phrase.strip().rstrip(".,;:!?")

        start = span.start_char + leading
        end = start + len(cleaned)

        return cleaned, start, end

    def get_phrase(self, token, doc):
        """Extract a clean noun phrase without surrounding punctuation."""

        for chunk in doc.noun_chunks:
            if chunk.start <= token.i < chunk.end:
                return self.clean_span(chunk)

        subtree = list(token.subtree)

        if not subtree:
            return (
                token.text,
                token.idx,
                token.idx + len(token.text)
            )

        start = min(item.i for item in subtree)
        end = max(item.i for item in subtree) + 1

        span = doc[start:end]

        return self.clean_span(span)

    def expand_conjuncts(self, token):
        """Expand coordinated subjects and objects."""

        result = []
        visited = set()
        stack = [token]

        while stack:
            current = stack.pop()

            if current.i in visited:
                continue

            visited.add(current.i)
            result.append(current)

            conjuncts = [
                child for child in current.children
                if child.dep_ == "conj"
            ]

            stack.extend(conjuncts)

        return sorted(result, key=lambda item: item.i)

    def extract_relations(self, text):
        """Extract relationships from input text."""

        doc = self.nlp_engine.process_text(text)
        relations = []
        seen = set()

        subject_dependencies = {
            "nsubj",
            "nsubjpass",
            "csubj"
        }

        object_dependencies = {
            "dobj",
            "obj",
            "attr",
            "oprd",
            "iobj"
        }

        for verb in doc:

            if verb.pos_ != "VERB":
                continue

            # Extract subjects, including coordinated subjects
            subject_tokens = []

            for child in verb.children:
                if child.dep_ in subject_dependencies:
                    subject_tokens.extend(
                        self.expand_conjuncts(child)
                    )

            # Extract direct objects, including coordinated objects
            object_tokens = []

            for child in verb.children:
                if child.dep_ in object_dependencies:
                    object_tokens.extend(
                        self.expand_conjuncts(child)
                    )

            # Remove duplicate tokens
            subject_tokens = list({
                token.i: token for token in subject_tokens
            }.values())

            object_tokens = list({
                token.i: token for token in object_tokens
            }.values())

            predicate = verb.lemma_.lower()

            # Create subject-predicate-object relationships
            for subject in subject_tokens:

                subject_text, subject_start, subject_end = (
                    self.get_phrase(subject, doc)
                )

                for obj in object_tokens:

                    object_text, object_start, object_end = (
                        self.get_phrase(obj, doc)
                    )

                    self.add_relation(
                        relations,
                        seen,
                        subject_text,
                        predicate,
                        object_text,
                        subject_start,
                        subject_end,
                        object_start,
                        object_end
                    )

            # Handle prepositional objects
            for prep in verb.children:

                if prep.dep_ != "prep":
                    continue

                for pobj in prep.children:

                    if pobj.dep_ != "pobj":
                        continue

                    coordinated_objects = self.expand_conjuncts(pobj)

                    for coordinated_obj in coordinated_objects:

                        object_text, object_start, object_end = (
                            self.get_phrase(coordinated_obj, doc)
                        )

                        for subject in subject_tokens:

                            subject_text, subject_start, subject_end = (
                                self.get_phrase(subject, doc)
                            )

                            prep_predicate = (
                                f"{predicate}_{prep.lemma_.lower()}"
                            )

                            self.add_relation(
                                relations,
                                seen,
                                subject_text,
                                prep_predicate,
                                object_text,
                                subject_start,
                                subject_end,
                                object_start,
                                object_end
                            )

        return relations

    @staticmethod
    def add_relation(
        relations,
        seen,
        subject,
        predicate,
        obj,
        subject_start,
        subject_end,
        object_start,
        object_end
    ):
        """Add a unique and clean relationship."""

        subject = subject.strip().rstrip(".,;:!?")
        obj = obj.strip().rstrip(".,;:!?")
        predicate = predicate.strip().lower()

        if not subject or not predicate or not obj:
            return

        if subject.casefold() == obj.casefold():
            return

        key = (
            subject.casefold(),
            predicate.casefold(),
            obj.casefold()
        )

        if key in seen:
            return

        seen.add(key)

        relations.append({
            "subject": subject,
            "predicate": predicate,
            "object": obj,
            "subject_start": subject_start,
            "subject_end": subject_end,
            "object_start": object_start,
            "object_end": object_end
        })

    def extract_triples(self, text):
        """Return relationships as subject-predicate-object triples."""

        relations = self.extract_relations(text)

        return [
            (
                relation["subject"],
                relation["predicate"],
                relation["object"]
            )
            for relation in relations
        ]


if __name__ == "__main__":

    extractor = RelationExtractor()

    sample_text = (
        "Google and Microsoft partnered with OpenAI and NVIDIA. "
        "Elon Musk founded SpaceX, Tesla, and Neuralink. "
        "SpaceX develops rocket technology."
    )

    relations = extractor.extract_relations(sample_text)

    print("\n========== RELATION EXTRACTION ==========")
    print("Total relationships:", len(relations))

    for index, relation in enumerate(relations, start=1):
        print(f"\nRelationship {index}")
        print("Subject:", relation["subject"])
        print("Predicate:", relation["predicate"])
        print("Object:", relation["object"])

    print("\n========== KNOWLEDGE TRIPLES ==========")

    for triple in extractor.extract_triples(sample_text):
        print(triple)
