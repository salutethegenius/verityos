from reranker_module import rank_chunks

# Dummy data
query_embedding = [0.1, 0.2, 0.3, 0.4]
indexed_chunks = [
    {
        "id": "chunk1",
        "text": "This is a test about email summaries.",
        "embedding": [0.1, 0.2, 0.3, 0.4],
        "agent": "ripple",
        "source": "inbox.md",
        "timestamp": "2025-05-22T17:00:00"
    },
    {
        "id": "chunk2",
        "text": "Unrelated information about finances.",
        "embedding": [0.4, 0.3, 0.2, 0.1],
        "agent": "minty",
        "source": "ledger.md",
        "timestamp": "2025-05-22T17:05:00"
    }
]

# Run ranking
results = rank_chunks(query_embedding, indexed_chunks)

# Show output
for result in results:
    print(f"\n[🔍 SCORE: {result['score']:.4f}]")
    print(f"Agent: {result['agent']} | Source: {result['source']}")
    print(f"Text: {result['text']}")