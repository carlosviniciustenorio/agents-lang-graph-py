import faiss
import re
import numpy as np
from sentence_transformers import SentenceTransformer


def smart_chunk(text, max_length=120):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) <= max_length:
            current += s + " "
        else:
            chunks.append(current.strip())
            current = s + " "
    if current:
        chunks.append(current.strip())
    return chunks


docs_raw = [
    "Camaro is a fast car",
    "Ferrari is an excellent car in terms of engine",
    "BMW is known for comfort and performance"
]

docs = []
for d in docs_raw:
    docs.extend(smart_chunk(d))


embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embeddings = embedder.encode(docs)

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings))


def retrieve(query: str, k: int = 2) -> str:
    q_emb = embedder.encode([query])
    _, ids = index.search(np.array(q_emb), k)
    return "\n".join(docs[i] for i in ids[0])
