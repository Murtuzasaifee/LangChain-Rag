"""
Debug script to test Google Drive API access
"""
from dotenv import load_dotenv
import os

load_dotenv()

# Test 1: Check if credentials exist
print("=" * 50)
print("TEST 1: Checking credentials files")
print("=" * 50)

creds_path = os.getenv("GOOGLE_ACCOUNT_FILE", "../credentials.json")
token_path = "../token.json"

print(f"Credentials path: {creds_path}")
print(f"Credentials exist: {os.path.exists(creds_path)}")
print(f"Token path: {token_path}")
print(f"Token exist: {os.path.exists(token_path)}")
print()

# Test 2: Try to authenticate directly with Google Drive API
print("=" * 50)
print("TEST 2: Direct Google Drive API test")
print("=" * 50)

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    import json

    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    creds = None
    # Load token if it exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        print("✅ Loaded existing token")
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🔐 Need to authenticate - opening browser...")
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print("✅ Token saved")
    
    # Build the Drive service
    service = build('drive', 'v3', credentials=creds)
    print("✅ Google Drive service initialized")
    print()
    
    # Test 3: List all files in root
    print("=" * 50)
    print("TEST 3: Listing files in 'My Drive' root")
    print("=" * 50)
    
    results = service.files().list(
        q="'root' in parents and trashed=false",
        pageSize=10,
        fields="files(id, name, mimeType)"
    ).execute()
    
    files = results.get('files', [])
    print(f"Found {len(files)} files/folders in root:")
    for f in files:
        print(f"  - {f['name']} (ID: {f['id']}, Type: {f['mimeType']})")
    print()
    
    # Test 4: Check specific folder
    print("=" * 50)
    print("TEST 4: Checking specific folder")
    print("=" * 50)
    
    folder_id = "1x_vHYamawB-f2aVdZbzSjVO0gbAqI_l7"
    print(f"Folder ID: {folder_id}")
    
    try:
        # Get folder metadata
        folder = service.files().get(fileId=folder_id, fields="id, name, mimeType, owners").execute()
        print(f"✅ Folder found: {folder['name']}")
        print(f"   MIME type: {folder['mimeType']}")
        if 'owners' in folder:
            print(f"   Owner: {folder['owners'][0].get('emailAddress', 'Unknown')}")
        print()
        
        # List files in the folder
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            pageSize=100,
            fields="files(id, name, mimeType, size)"
        ).execute()
        
        files = results.get('files', [])
        print(f"Found {len(files)} files in this folder:")
        for f in files:
            size = int(f.get('size', 0)) if 'size' in f else 0
            size_mb = size / (1024 * 1024)
            print(f"  - {f['name']}")
            print(f"    ID: {f['id']}")
            print(f"    Type: {f['mimeType']}")
            print(f"    Size: {size_mb:.2f} MB")
        print()
        
    except Exception as e:
        print(f"❌ Error accessing folder: {e}")
        print("   Possible reasons:")
        print("   1. Folder ID is incorrect")
        print("   2. Folder is not shared with the authenticated account")
        print("   3. Folder was deleted")
        print()
    
    # Test 5: Try LangChain retriever
    print("=" * 50)
    print("TEST 5: Testing LangChain GoogleDriveRetriever")
    print("=" * 50)
    
    from langchain_googledrive.retrievers import GoogleDriveRetriever
    
    retriever = GoogleDriveRetriever(
        template="gdrive-all-in-folder",
        folder_id=folder_id,
        num_results=10,
    )
    
    docs = retriever.invoke("")
    print(f"LangChain retrieved {len(docs)} documents")
    
    for i, doc in enumerate(docs, 1):
        print(f"\nDocument {i}:")
        print(f"  Title: {doc.metadata.get('title', 'Untitled')}")
        print(f"  Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"  Content length: {len(doc.page_content)} chars")
        print(f"  Content preview: {doc.page_content[:100]}...")
    
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
