import chromadb
import hashlib

class KnowledgeDB:
    def __init__(self, db_path="data/nova_knowledge.db", chroma_path="data/knowledge_vectors"):
        # Fix 1: KnowledgeDB uses a separate PersistentClient with ALAG path
        self.chroma = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.chroma.get_or_create_collection("nova_knowledge")
        self.db_path = db_path

    def search(self, question: str):
        res = self.collection.query(query_texts=[question], n_results=1)
        # Check similarity (distance < 0.15 is roughly > 0.85 similarity)
        if res['distances'] and res['distances'][0] and res['distances'][0][0] < 0.15:
            return res['documents'][0][0]
        return None

    def save(self, question: str, answer: str):
        doc_id = hashlib.md5(question.encode()).hexdigest()
        self.collection.upsert(
            documents=[answer],
            metadatas=[{"question": question}],
            ids=[doc_id]
        )
