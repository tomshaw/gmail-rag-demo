import chromadb

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chromadb")

def delete_collection(collection_name: str):
    """Delete a collection from ChromaDB"""
    try:
        chroma_client.delete_collection(name=collection_name)
        print(f"Collection '{collection_name}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting collection '{collection_name}': {e}")

if __name__ == '__main__':
    collection_name = "email_collection"
    delete_collection(collection_name)