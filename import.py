import argparse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import chromadb
from chromadb.utils import embedding_functions
import os.path
from typing import List, Dict
import base64
from bs4 import BeautifulSoup
import html

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chromadb")
# Use sentence-transformers for embeddings
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
# Create or get collection
email_collection = chroma_client.get_or_create_collection(
    name="email_collection",
    embedding_function=embedding_function,
    metadata={"hnsw:space": "cosine"}
)

def authenticate_gmail():
    """Authenticate with Gmail API using OAuth 2.0"""
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def get_email_metadata(msg) -> Dict:
    """Extract metadata from email message"""
    headers = msg['payload']['headers']
    metadata = {
        'message_id': msg['id'],
        'thread_id': msg['threadId'],
        'date': next((h['value'] for h in headers if h['name'] == 'Date'), ''),
        'from': next((h['value'] for h in headers if h['name'] == 'From'), ''),
        'subject': next((h['value'] for h in headers if h['name'] == 'Subject'), '')
    }
    return metadata

def get_email_body(msg) -> str:
    """Extract and clean email body from message"""
    if 'parts' in msg['payload']:
        parts = msg['payload']['parts']
        body = ""
        for part in parts:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode()
                    break
            elif part['mimeType'] == 'text/html':
                if 'data' in part['body']:
                    html_content = base64.urlsafe_b64decode(part['body']['data']).decode()
                    # Convert HTML to plain text
                    soup = BeautifulSoup(html_content, 'html.parser')
                    body = soup.get_text(separator=' ', strip=True)
                    break
    else:
        # Handle messages with no parts
        if 'data' in msg['payload']['body']:
            body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode()
            if msg['payload']['mimeType'] == 'text/html':
                soup = BeautifulSoup(body, 'html.parser')
                body = soup.get_text(separator=' ', strip=True)
    
    # Clean up the text
    body = html.unescape(body)  # Handle HTML entities
    body = ' '.join(body.split())  # Normalize whitespace
    return body

def get_emails_from_label(service, label_name='INBOX', limit=10):
    label_name = label_name.replace('\\', '/')
    
    labels = service.users().labels().list(userId='me').execute().get('labels', [])
    label_id = next((label['id'] for label in labels if label['name'] == label_name), None)
    if not label_id:
        print(f"Label {label_name} not found.")
        return []

    results = service.users().messages().list(userId='me', labelIds=[label_id], maxResults=limit).execute()
    messages = results.get('messages', [])
    
    email_data = []
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        metadata = get_email_metadata(msg)
        body = get_email_body(msg)
        
        # Create a combined text for embedding
        full_text = f"Subject: {metadata['subject']}\n\n{body}"
        
        # Add additional metadata
        additional_metadata = {
            "type": "email",
            "date": metadata['date'],
            "subject": metadata['subject']
        }
        metadata.update(additional_metadata)
        
        # Check if email already exists in ChromaDB
        existing = email_collection.get(
            where={"message_id": metadata['message_id']},
            limit=1
        )
        
        if not existing['ids']:  # Email doesn't exist in ChromaDB
            # Add to ChromaDB
            email_collection.add(
                documents=[full_text],
                metadatas=[metadata],
                ids=[metadata['message_id']]
            )
        
        email_data.append({"body": body, "metadata": metadata})

    return email_data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch and query emails from Gmail')
    parser.add_argument('--label', type=str, default='INBOX',
                       help='Gmail label to fetch emails from (default: INBOX)')
    parser.add_argument('--limit', type=int, default=10,
                       help='Maximum number of emails to fetch (default: 10)')
    
    args = parser.parse_args()
    
    service = authenticate_gmail()
    emails = get_emails_from_label(service, label_name=args.label, limit=args.limit)
    print(f"Processed {len(emails)} emails")
    
    for email in emails:
        print(f"Subject: {email['metadata']['subject']}")
        print(f"Body: {email['body']}\n")