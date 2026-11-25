
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

client = OpenAI(
    api_key=__import__("os").getenv("NVIDIA_API_KEY"),
    base_url=__import__("os").getenv(
        "NVIDIA_BASE_URL",
        "https://integrate.api.nvidia.com/v1"
    ),
    timeout=120
)

model = __import__("os").getenv(
    "NVIDIA_MODEL",
    "nvidia/nemotron-3.5-lightning-30b-a3b"
)

source = (BASE_DIR / "hallucination_test.txt").read_text(
    encoding="utf-8"
)

prompt = f"""
Extract only factual subject-relation-object triples
explicitly supported by the document.

Return valid JSON only:
{{"triples":[{{"subject":"Company Alpha",
"relation":"developed","object":"Product Z"}}]}}

Do not turn negated, denied, or explicitly unsupported
relationships into facts. Do not infer missing facts.

DOCUMENT:
{source}
"""

response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": "Extract source-grounded facts. Return JSON only."
        },
        {"role": "user", "content": prompt}
    ],
    temperature=0,
    max_tokens=2000
)

content = response.choices[0].message.content or ""
start = content.find("{")
end = content.rfind("}")

if start == -1 or end < start:
    raise ValueError("Model did not return valid JSON:\n" + content)

data = json.loads(content[start:end + 1])
triples = data.get("triples", [])

print("\n--- Hallucination Test Results ---")
for triple in triples:
    print(
        f"{triple.get('subject')} --"
        f"[{triple.get('relation')}]--> "
        f"{triple.get('object')}"
    )

hallucinations = [
    t for t in triples
    if t.get("subject", "").casefold() == "company alpha"
    and t.get("relation", "").casefold() == "acquired"
    and t.get("object", "").casefold() == "company beta"
]

if hallucinations:
    print("\nRESULT: Unsupported acquisition relation detected.")
    print("This is a potential hallucination.")
else:
    print("\nRESULT: Unsupported acquisition relation not extracted.")

print("Manually verify every extracted triple against the document.")
