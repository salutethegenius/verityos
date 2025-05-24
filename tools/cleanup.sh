#!/bin/bash

echo "🧹 Phase 1: Safe cleanup starting..."

# Create folders if they don’t exist
mkdir -p scripts
mkdir -p tools
mkdir -p archive
mkdir -p memory_system/verity

# Move helper scripts to /scripts
for file in embedder.py core.py vault.py; do
  if [ -f "$file" ]; then
    echo "📁 Moving $file to scripts/"
    mv "$file" scripts/
  fi
done

# Move root-level memory.txt if found
if [ -f memory.txt ]; then
  echo "📁 Moving memory.txt to memory_system/verity/"
  mv memory.txt memory_system/verity/
fi

# Archive stray/duplicate files
if [ -f memory_system/verity/long_term_docs.pk1 ]; then
  echo "📦 Archiving long_term_docs.pk1"
  mv memory_system/verity/long_term_docs.pk1 archive/
fi

# Archive legacy /agents/verity/memory if exists
if [ -d agents/verity/memory ]; then
  echo "📦 Archiving agents/verity/memory"
  mv agents/verity/memory archive/verity_memory_backup
fi

# Archive /memory folder for now, don't delete yet
if [ -d memory ]; then
  echo "📦 Archiving top-level /memory folder"
  mv memory archive/memory_backup
fi

echo "✅ Phase 1 safe cleanup done."
echo "Next: Update file paths in boot.py, memory_core.py, and any agents referencing old memory."cl