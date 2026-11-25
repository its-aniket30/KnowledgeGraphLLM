
import json
import re

def normalize(text):
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text

def normalize_triple(subject, relation, obj):
    subject = normalize(subject)
    relation = normalize(relation)
    obj = normalize(obj)

    # Normalize equivalent relation wording
    if relation in ("is a", "is an"):
        relation = "is"

    # Normalize articles at the beginning of the object
    obj = re.sub(r"^(a|an)\s+", "", obj)

    return (subject, relation, obj)

# Load extracted triples
with open("triples.json", "r", encoding="utf-8") as f:
    data = json.load(f)

extracted = {
    normalize_triple(t["subject"], t["relation"], t["object"])
    for t in data
}

# Manually prepared reference triples
reference_data = [
    ("Google", "developed", "Gemini"),
    ("Gemini", "is", "an artificial intelligence model"),
    ("OpenAI", "developed", "ChatGPT"),
    ("ChatGPT", "is", "an artificial intelligence model"),
    ("Python", "is used for", "machine learning"),
    ("NetworkX", "is", "a Python library for creating and analyzing graphs"),
]

reference = {
    normalize_triple(s, r, o)
    for s, r, o in reference_data
}

correct = extracted & reference
incorrect = extracted - reference
missed = reference - extracted

precision = len(correct) / len(extracted) if extracted else 0
recall = len(correct) / len(reference) if reference else 0
f1 = (
    2 * precision * recall / (precision + recall)
    if precision + recall else 0
)

print("\n=============================================")
print(" KNOWLEDGE GRAPH EXTRACTION VALIDATION")
print("=============================================")
print(f"Reference triples : {len(reference)}")
print(f"Extracted triples : {len(extracted)}")
print(f"Correct triples   : {len(correct)}")
print(f"Incorrect triples : {len(incorrect)}")
print(f"Missed triples    : {len(missed)}")

print("\n--- Evaluation Metrics ---")
print(f"Precision : {precision:.2%}")
print(f"Recall    : {recall:.2%}")
print(f"F1-score  : {f1:.2%}")

if incorrect:
    print("\n--- Incorrect or Extra Triples ---")
    for s, r, o in sorted(incorrect):
        print(f"{s} -> {r} -> {o}")

if missed:
    print("\n--- Missed Reference Triples ---")
    for s, r, o in sorted(missed):
        print(f"{s} -> {r} -> {o}")

print("\nNote: Article and relation wording are normalized.")
print("These metrics apply only to this reference dataset.")
print("Manually verify every triple against the source text.")
print("\nValidation completed.")
