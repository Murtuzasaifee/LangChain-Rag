"""
Test GoogleDriveLoader as an alternative to GoogleDriveRetriever
"""
from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("TEST: Using GoogleDriveLoader (Document Loader)")
print("=" * 60)

try:
    from langchain_community.document_loaders import GoogleDriveLoader
    
    folder_id = "1x_vHYamawB-f2aVdZbzSjVO0gbAqI_l7"
    
    # Try loading documents from the folder
    loader = GoogleDriveLoader(
        folder_id=folder_id,
        recursive=False,  # Don't search subfolders
        file_types=["pdf"],  # Specify file types (txt not supported)
    )
    
    docs = loader.load()
    print(f"✅ Loaded {len(docs)} documents")
    
    for i, doc in enumerate(docs, 1):
        print(f"\n  Document {i}:")
        print(f"    Metadata: {doc.metadata}")
        print(f"    Content length: {len(doc.page_content)} chars")
        print(f"    Content preview: {doc.page_content[:200]}...")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST 2: Check token scopes")
print("=" * 60)

try:
    from google.oauth2.credentials import Credentials
    import json
    
    token_path = "../token.json"
    with open(token_path, 'r') as f:
        token_data = json.load(f)
    
    print(f"Token scopes: {token_data.get('scopes', 'No scopes found')}")
    
    creds = Credentials.from_authorized_user_file(token_path)
    print(f"Valid: {creds.valid}")
    print(f"Expired: {creds.expired}")
    
except Exception as e:
    print(f"❌ Error: {e}")
