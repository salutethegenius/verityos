from pathlib import Path
import time
import numpy as np
import faiss
import requests
import json
import traceback
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")

# Ensure the embedded folder exists
BASE_DIR = Path(__file__).resolve().parent.parent.parent
EMBED_DIR = BASE_DIR / 'data' / 'embedded'
EMBED_DIR.mkdir(parents=True, exist_ok=True)

def chunk_text(text, size=500, is_csv=False):
    if is_csv:
        return [line.strip() for line in text.splitlines() if line.strip()]
    return [text[i:i+size] for i in range(0, len(text), size) if text[i:i+size].strip()]

# === Paths for vector DB ===
index_path = EMBED_DIR / "faiss_index.bin"
mapping_path = EMBED_DIR / "vector_mapping.json"


# === Embedding function using external API ===
def get_embedding(text):
    return model.encode(text)

# === Index helpers ===
def load_or_create_index():
    if index_path.exists() and mapping_path.exists():
        index = faiss.read_index(str(index_path))
        with open(mapping_path, "r") as f:
            mapping = json.load(f)
    else:
        # Dynamically set index dimension from first test embedding
        test_vec = get_embedding("test")
        dim = len(test_vec)
        index = faiss.IndexFlatL2(dim)
        mapping = []
    return index, mapping

def save_index(index, mapping):
    faiss.write_index(index, str(index_path))
    with open(mapping_path, "w") as f:
        json.dump(mapping, f)
    print(f"✅ FAISS index saved to {index_path}")
    print(f"✅ Mapping saved to {mapping_path}")

# === Embed a single file ===
def embed_file(file_path: str) -> str:
    file = Path(file_path)
    if not file.exists() or not file.is_file():
        return f"❌ File not found: {file_path}"

    try:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        is_csv = file.suffix.lower() == ".csv"
        chunks = chunk_text(content, is_csv=is_csv)
        chunks = [c for c in chunks if len(c.strip().split(",")) > 2 and not c.lower().startswith("category") and not c.lower().startswith("description")]
        index, mapping = load_or_create_index()
        start_time = time.time()
        for idx, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            elapsed = time.time() - start_time
            avg_time = elapsed / (idx + 1)
            remaining = avg_time * (len(chunks) - (idx + 1))
            print(f"⏳ Embedding chunk {idx + 1}/{len(chunks)} — ETA: {int(remaining)}s", end="\r")
            embedding = np.array([get_embedding(chunk)]).astype('float32')
            if embedding.shape[1] != index.d:
                print(f"❌ Skipping chunk due to dimension mismatch: got {embedding.shape[1]}, expected {index.d}")
                continue
            index.add(embedding)
            line = chunk.strip()
            amount = None
            date = None
            try:
                parts = [p.strip() for p in line.split(",")]
                for p in parts:
                    if "$" in p or p.replace(".", "").isdigit():
                        try:
                            amount = float(p.replace("$", "").strip())
                        except:
                            pass
                    if any(month in p.lower() for month in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]):
                        date = p
            except:
                pass

            mapping.append({
                "file": file.name,
                "text": line,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "amount": amount,
                "date": date,
                "source_type": (
                    "memory" if file.suffix.lower() == ".txt"
                    else "invoice" if "invoice" in file.name.lower()
                    else "summary"
                )
            })
        save_index(index, mapping)
        return f"✅ Embedded {len(chunks)} chunks from {file.name}"
    except Exception as e:
        error_detail = traceback.format_exc()
        return f"❌ Error embedding file {file.name}: {str(e)}\n{error_detail}"

# === Embed all files in a folder ===
def embed_folder(folder_path: str) -> str:
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        return f"❌ Folder not found: {folder_path}"

    index, mapping = load_or_create_index()
    embedded_files = []

    for file in folder.glob("*"):
        if file.is_file():
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                is_csv = file.suffix.lower() == ".csv"
                chunks = chunk_text(content, is_csv=is_csv)
                chunks = [c for c in chunks if len(c.strip().split(",")) > 2 and not c.lower().startswith("category") and not c.lower().startswith("description")]
                start_time = time.time()
                for idx, chunk in enumerate(chunks):
                    if not chunk.strip():
                        continue
                    elapsed = time.time() - start_time
                    avg_time = elapsed / (idx + 1)
                    remaining = avg_time * (len(chunks) - (idx + 1))
                    print(f"⏳ {file.name}: chunk {idx + 1}/{len(chunks)} — ETA: {int(remaining)}s", end="\r")
                    embedding = np.array([get_embedding(chunk)]).astype('float32')
                    if embedding.shape[1] != index.d:
                        print(f"❌ Skipping chunk due to dimension mismatch: got {embedding.shape[1]}, expected {index.d}")
                        continue
                    index.add(embedding)
                    line = chunk.strip()
                    amount = None
                    date = None
                    try:
                        parts = [p.strip() for p in line.split(",")]
                        for p in parts:
                            if "$" in p or p.replace(".", "").isdigit():
                                try:
                                    amount = float(p.replace("$", "").strip())
                                except:
                                    pass
                            if any(month in p.lower() for month in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]):
                                date = p
                    except:
                        pass

                    mapping.append({
                        "file": file.name,
                        "text": line,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "amount": amount,
                        "date": date,
                        "source_type": (
                            "memory" if file.suffix.lower() == ".txt"
                            else "invoice" if "invoice" in file.name.lower()
                            else "summary"
                        )
                    })
                embedded_files.append(f"{file.name}: ✅ {len(chunks)} chunks embedded")
            except Exception as e:
                error_detail = traceback.format_exc()
                embedded_files.append(f"{file.name}: ❌ {str(e)}\n{error_detail}")

    save_index(index, mapping)
    return "📚 Folder Embed Results:\n" + "\n".join(embedded_files)

# === Query embedded knowledge ===
def query_text(query: str, top_k: int = 3) -> str:
    index, mapping = load_or_create_index()
    if index.ntotal == 0:
        return "⚠️ No embedded knowledge available."

    query_vec = np.array([get_embedding(query)]).astype('float32')
    distances, indices = index.search(query_vec, top_k)

    results = []
    for rank, i in enumerate(indices[0], start=1):
        if 0 <= i < len(mapping):
            entry_data = mapping[i]
            text = entry_data["text"].strip().replace("\n", " ") if isinstance(entry_data, dict) else entry_data.strip().replace("\n", " ")
            short_entry = text[:400] + ("..." if len(text) > 400 else "")
            results.append(f"{rank}. {short_entry}")

    return "🔍 Query Results:\n\n" + "\n\n".join(results)

# === Show knowledge map ===
def show_knowledge_map():
    try:
        keywords_file = EMBED_DIR / "keywords.txt"
        if not keywords_file.exists():
            return "❌ No knowledge map found."
        return "🧠 Knowledge Map:\n" + keywords_file.read_text()
    except Exception as e:
        return f"🔥 Error reading knowledge map: {e}"


# === Advanced Query with Filters and Totals ===
def query_advanced(query: str) -> str:
    index, mapping = load_or_create_index()
    if not mapping:
        return "⚠️ No embedded data to search."

    query_lower = query.lower()
    target_year = None
    if "20" in query_lower:
        for word in query_lower.split():
            if word.startswith("20") and word.isdigit():
                target_year = word

    filtered = mapping
    # Prioritize entries with "source_type": "invoice" or "memory"
    filtered = [m for m in filtered if isinstance(m, dict) and m.get("source_type") in ["invoice", "memory"]]
    if target_year:
        filtered = [m for m in filtered if isinstance(m, dict) and m.get("date") and target_year in m.get("date")]

    if "how much" in query_lower or "total" in query_lower:
        total = sum(float(m.get("amount", 0)) for m in filtered if isinstance(m, dict) and m.get("amount") is not None)
        return f"💰 Total earnings in {target_year if target_year else 'all years'}: ${total:.2f}"

    entries = [
        f"{m.get('date', 'No Date')} — {m.get('text', '')[:200]}..."
        for m in filtered[:5]
        if isinstance(m, dict)
    ]
    return "🔍 Filtered Results:\n\n" + "\n\n".join(entries) if entries else "⚠️ No matches found."