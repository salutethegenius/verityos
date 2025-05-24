import math

def cosine_similarity(vec1, vec2):
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def rank_chunks(query_embedding, indexed_chunks, top_k=5):
    scored_chunks = []
    for chunk in indexed_chunks:
        if "embedding" not in chunk:
            continue
        score = cosine_similarity(query_embedding, chunk["embedding"])
        scored_chunks.append({
            "text": chunk.get("text", ""),
            "score": score,
            "agent": chunk.get("agent", "unknown"),
            "source": chunk.get("source", "unknown"),
            "chunk_id": chunk.get("id", "unknown"),
            "timestamp": chunk.get("timestamp", "unknown")
        })

    ranked = sorted(scored_chunks, key=lambda x: x["score"], reverse=True)
    return ranked[:top_k]