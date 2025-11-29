"""
Test GoogleDriveRetriever with different templates
"""
from dotenv import load_dotenv
load_dotenv()

from langchain_googledrive.retrievers import GoogleDriveRetriever

folder_id = "1x_vHYamawB-f2aVdZbzSjVO0gbAqI_l7"

print("=" * 60)
print("TEST 1: gdrive-all-in-folder (get all files)")
print("=" * 60)
try:
    retriever = GoogleDriveRetriever(
        template="gdrive-all-in-folder",
        folder_id=folder_id,
        num_results=10,
    )
    docs = retriever.invoke("")
    print(f"✅ Retrieved {len(docs)} documents")
    for i, doc in enumerate(docs, 1):
        print(f"\n  Document {i}:")
        print(f"    Title: {doc.metadata.get('title', 'Untitled')}")
        print(f"    Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"    Content length: {len(doc.page_content)} chars")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST 2: gdrive-query (search everywhere)")
print("=" * 60)
try:
    retriever = GoogleDriveRetriever(
        template="gdrive-query",
        num_results=10,
    )
    docs = retriever.invoke("RAG")
    print(f"✅ Retrieved {len(docs)} documents for query 'RAG'")
    for i, doc in enumerate(docs, 1):
        print(f"\n  Document {i}:")
        print(f"    Title: {doc.metadata.get('title', 'Untitled')}")
        print(f"    Source: {doc.metadata.get('source', 'Unknown')}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("TEST 3: gdrive-query-in-folder")
print("=" * 60)
try:
    retriever = GoogleDriveRetriever(
        template="gdrive-query-in-folder",
        folder_id=folder_id,
        num_results=10,
    )
    docs = retriever.invoke("attention")
    print(f"✅ Retrieved {len(docs)} documents for query 'attention'")
    for i, doc in enumerate(docs, 1):
        print(f"\n  Document {i}:")
        print(f"    Title: {doc.metadata.get('title', 'Untitled')}")
        print(f"    Source: {doc.metadata.get('source', 'Unknown')}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("TEST 4: gdrive-mime-type (PDFs only)")
print("=" * 60)
try:
    retriever = GoogleDriveRetriever(
        template="gdrive-mime-type",
        mime_type="application/pdf",
        num_results=10,
    )
    docs = retriever.invoke("")
    print(f"✅ Retrieved {len(docs)} PDF documents")
    for i, doc in enumerate(docs, 1):
        print(f"\n  Document {i}:")
        print(f"    Title: {doc.metadata.get('title', 'Untitled')}")
        print(f"    Source: {doc.metadata.get('source', 'Unknown')}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("TEST 5: Direct API call to verify files exist")
print("=" * 60)
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

token_path = "../token.json"
creds = Credentials.from_authorized_user_file(token_path)
service = build('drive', 'v3', credentials=creds)

results = service.files().list(
    q=f"'{folder_id}' in parents and trashed=false",
    pageSize=100,
    fields="files(id, name, mimeType)"
).execute()

files = results.get('files', [])
print(f"✅ Direct API found {len(files)} files:")
for f in files:
    print(f"  - {f['name']} ({f['mimeType']})")
