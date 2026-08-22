import sqlite3
import chromadb

def cleanup():
    # 1. Delete from SQLite
    try:
        conn = sqlite3.connect("data/nova_knowledge.db")
        conn.execute("""
            DELETE FROM knowledge 
            WHERE question LIKE '%chief minister%'
            OR question LIKE '%uttar pradesh%'
        """)
        conn.commit()
        print("Deleted wrong entries from SQLite")
        conn.close()
    except Exception as e:
        print("Error with SQLite:", e)

    # 2. Delete from ChromaDB (optional but good to keep in sync)
    try:
        client = chromadb.PersistentClient(path="./data/chroma_db")
        collection = client.get_collection(name="nova_knowledge")
        results = collection.get(where_document={"$contains": "uttar pradesh"})
        if results and results["ids"]:
            collection.delete(ids=results["ids"])
            print("Deleted wrong entries from ChromaDB")
    except Exception as e:
        print("Error with ChromaDB:", e)

if __name__ == "__main__":
    cleanup()
