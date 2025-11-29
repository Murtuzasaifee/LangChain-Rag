"""
Re-authenticate with proper Google Drive scopes
This will delete the old token and create a new one with the correct permissions
"""
import os

# Delete the old token
token_path = "../token.json"
if os.path.exists(token_path):
    os.remove(token_path)
    print(f"✅ Deleted old token: {token_path}")

# Now authenticate with the correct scopes
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# These are the scopes needed for GoogleDriveRetriever
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

print("\n" + "=" * 60)
print("Authenticating with Google Drive...")
print("Scopes requested:")
for scope in SCOPES:
    print(f"  - {scope}")
print("=" * 60)

creds_path = "../credentials.json"

# Run the OAuth flow
flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
creds = flow.run_local_server(port=0)

# Save the credentials
with open(token_path, 'w') as token:
    token.write(creds.to_json())

print(f"\n✅ New token saved to: {token_path}")
print("\nYou can now use GoogleDriveRetriever!")

# Test the connection
print("\n" + "=" * 60)
print("Testing connection...")
print("=" * 60)

service = build('drive', 'v3', credentials=creds)

# List files in root
results = service.files().list(
    pageSize=5,
    fields="files(id, name, mimeType)"
).execute()

files = results.get('files', [])
print(f"\n✅ Successfully connected! Found {len(files)} files in your Drive:")
for f in files[:5]:
    print(f"  - {f['name']} ({f['mimeType']})")
