import argparse
import chromadb
from chromadb.utils import embedding_functions

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chromadb")
# Use sentence-transformers for embeddings
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
# Get the collection
email_collection = chroma_client.get_collection(name="email_collection")

def query_emails(query: str, n_results: int = 5):
    """Query emails using ChromaDB"""
    results = email_collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Query emails from ChromaDB')
    parser.add_argument('--query', type=str, required=True, help='Query to search through emails')
    parser.add_argument('--limit', type=int, default=5, help='Maximum number of results to return (default: 5)')
    
    args = parser.parse_args()
    
    results = query_emails(args.query, args.limit)
    
    print(f"Query: {args.query}")
    print(f"Returned {len(results['documents'][0])} results:")
    
    for i, doc in enumerate(results['documents'][0]):
        print(f"{i+1}. Subject: {results['metadatas'][0][i]['subject']}")