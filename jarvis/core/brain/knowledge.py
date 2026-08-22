"""
jarvis/core/brain/knowledge.py
Knowledge Base for NOVA. Indexes local files (PDF, TXT) into ChromaDB.
"""

import os
import PyPDF2
from jarvis.core.brain.memory import LongTermMemory

class KnowledgeBase:
    def __init__(self, memory_engine: LongTermMemory):
        self.memory = memory_engine

    def index_file(self, file_path: str) -> str:
        """Reads a file and stores its content in the owner_facts memory."""
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' nahi mili, Sir."

        ext = os.path.splitext(file_path)[1].lower()
        content = ""

        try:
            if ext == ".txt":
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif ext == ".pdf":
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        content += page.extract_text() + "\n"
            else:
                return f"Maaf kijiye, abhi main sirf .txt aur .pdf files hi padh sakti hoon."

            if not content.strip():
                return f"File '{file_path}' khali lag rahi hai."

            # Chunking (simple)
            chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
            for i, chunk in enumerate(chunks):
                self.memory.store_fact(f"KNOWLEDGE FROM {os.path.basename(file_path)} (Part {i+1}): {chunk}")

            return f"File '{os.path.basename(file_path)}' ko maine yaad kar liya hai, Sir."
        except Exception as e:
            return f"File padhne mein error aaya: {e}"

    def search_knowledge(self, query: str) -> str:
        """Alias for retrieving from long-term memory."""
        return self.memory.retrieve_relevant(query)
