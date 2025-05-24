import os
import json
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from typing import List
from tqdm import tqdm

# Paths
BASE_PATH = "/home/ubuntu/verityos/"
STM_PATH = os.path.join(BASE_PATH, "memory_system/verity/short_term.json")
LTM_INDEX_PATH = os.path.join(BASE_PATH, "memory_system/verity/long_term_index.faiss")
LTM_DOCS_PATH = os.path.join(BASE_PATH, "memory_system/verity/long_term_docs.pkl")
LOG_DIR = os.path.join(BASE_PATH, "logs")
LOG_PATH = os.path.join(LOG_DIR, "indexing.log")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Model for embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_query_embedding(text: str):
    return model.encode(text)

# Short-Term Memory Functions
def load_short_term_memory():
    if not os.path.exists(STM_PATH):
        return []
    with open(STM_PATH, "r") as f:
        return json.load(f)

def save_short_term_memory(memory: List[str]):
    with open(STM_PATH, "w") as f:
        json.dump(memory[-20:], f, indent=2)  # keep last 20 entries

def add_to_short_term_memory(entry: str):
    memory = load_short_term_memory()
    memory.append(entry)
    save_short_term_memory(memory)

# Long-Term Memory Functions
def build_index_from_folder(folder_path: str, verbose: bool = False):
    import re
    from datetime import datetime

    texts = []
    sources = []
    publish_dates = []
    scrape_dates = []
    for root, _, files in os.walk(folder_path):
        for file in tqdm(files, desc="📚 Embedding Files"):
            if file.endswith(".md") or file.endswith(".txt"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    content = re.sub(r"\*\*Date:\*\* \d{4}-\d{2}-\d{2}", "", content)
                    date_match = re.search(r"\*\*Date:\*\* (\d{4}-\d{2}-\d{2})", content)
                    publish_date = date_match.group(1) if date_match else "unknown"
                    scrape_date = os.path.basename(filepath).split("-")[0:3]
                    scrape_date = "-".join(scrape_date) if len(scrape_date) == 3 else datetime.today().strftime('%Y-%m-%d')
                    with open(LOG_PATH, "a") as log:
                        log.write(f"{file} | {len(content)} chars\n")
                    if verbose:
                        print(f"Processing file: {file}")
                        print(f"Character count: {len(content)}")
                    texts.append(content)
                    sources.append(filepath)
                    publish_dates.append(publish_date)
                    scrape_dates.append(scrape_date)

    if not texts:
        print("No valid files found.")
        return []

    embeddings = model.encode(texts, convert_to_tensor=False)
    index = faiss.IndexFlatL2(len(embeddings[0]))
    index.add(embeddings)

    with open(LTM_DOCS_PATH, "wb") as f:
        pickle.dump(sources, f)

    faiss.write_index(index, LTM_INDEX_PATH)
    print(f"✅ Built index with {len(texts)} documents.")

    # Return chunk data for JSON-based RAG
    chunks = []
    for text, embed, path, publish_date, scrape_date in tqdm(zip(texts, embeddings, sources, publish_dates, scrape_dates), desc="🧩 Chunking", total=len(texts)):
        with open(LOG_PATH, "a") as log:
            log.write(f"🧩 Chunked {os.path.basename(path)} | {len(text)} chars | Publish: {publish_date} | Scrape: {scrape_date}\n")
        chunks.append({
            "text": text,
            "embedding": embed.tolist(),
            "source": path,
            "publish_date": publish_date,
            "scrape_date": scrape_date
        })

    print(f"✅ Chunking complete: {len(texts)} total chunks.")
    with open(os.path.join(LOG_DIR, "lastindex.txt"), "w") as f:
        f.write(f"Agent: verity\n")
        f.write(f"Folder: {folder_path}\n")
        f.write(f"Chunks: {len(texts)}\n")
        f.write(f"Log: {LOG_PATH}\n")
        f.write(f"Completed: ✅\n")

    return chunks

def query_long_term_memory(query: str, top_k: int = 3):
    if not os.path.exists(LTM_INDEX_PATH) or not os.path.exists(LTM_DOCS_PATH):
        return []

    index = faiss.read_index(LTM_INDEX_PATH)
    with open(LTM_DOCS_PATH, "rb") as f:
        sources = pickle.load(f)

    query_vector = model.encode([query])
    D, I = index.search(query_vector, top_k)

    results = []
    for i in I[0]:
        path = sources[i]
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if isinstance(content, str):
                results.append(f"[From {path}]\n{content}")
            else:
                results.append(f"[From {path}]\n{json.dumps(content)}")
    return results

def get_combined_context(query: str):
    stm = load_short_term_memory()
    ltm_contents = query_long_term_memory(query)
    context = "Short-Term Memory:\n" + "\n".join(stm[-5:]) + "\n\nLong-Term Memory:\n" + "\n---\n".join(ltm_contents)
    return context