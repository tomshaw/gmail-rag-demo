import argparse
import chromadb
from chromadb.utils import embedding_functions
import json
from ollama import Client

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chromadb")
# Use sentence-transformers for embeddings
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
# Get the collection
email_collection = chroma_client.get_collection(name="email_collection")

def query_emails(query: str, n_results: int = 5, distance_threshold: float = 0.5):
    """Query emails using ChromaDB with a distance threshold"""
    results = email_collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    # Filter results based on distance threshold
    filtered_results = {
        'documents': [],
        'metadatas': [],
        'distances': []
    }
    
    for i, distance in enumerate(results['distances'][0]):
        if distance < distance_threshold:
            filtered_results['documents'].append(results['documents'][0][i])
            filtered_results['metadatas'].append(results['metadatas'][0][i])
            filtered_results['distances'].append(distance)
    
    return filtered_results

def create_queries(prompt: str):
    """Create queries using a simplified template"""
    query_msg = (
        "You are a political scientist AI agent. "
        "Respond with the relevant information as accurately as possible with several paragraphs answering the question."
    )

    query_convo = [
        {"role": "system", "content": query_msg},
        {"role": "user", "content": prompt}
    ]

    return query_convo

def generate_response(prompt: str):
    """Generate response using the local Llama model"""
    query_convo = create_queries(prompt)
    
    client = Client()
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in query_convo]
    
    for chunk in client.chat(model='llama3.1:8b', messages=messages, stream=True):
        print(chunk['message']['content'], end='')

def format_response(query: str, results):
    """Format the response based on multi-shot learning examples"""
    response = f"Query: {query}\n"
    response += f"Returned {len(results['documents'])} results:\n"
    
    for i, doc in enumerate(results['documents']):
        response += f"{i+1}. Subject: {results['metadatas'][i]['subject']}, Similarity Score: {results['distances'][i]}\n"
    
    return response

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Query emails from ChromaDB and generate response using Llama model')
    parser.add_argument('--query', type=str, required=True, help='Query to search through emails')
    parser.add_argument('--limit', type=int, default=5, help='Maximum number of results to return (default: 5)')
    parser.add_argument('--threshold', type=float, default=0.5, help='Distance threshold for filtering results (default: 0.5)')
    
    args = parser.parse_args()
    
    # Query emails from ChromaDB
    results = query_emails(args.query, args.limit, args.threshold)
    
    # Format the response
    formatted_response = format_response(args.query, results)
    
    # Print ChromaDB document subjects and similarity scores
    print(formatted_response)
    
    # Generate the final response using the Llama model
    generate_response(formatted_response)