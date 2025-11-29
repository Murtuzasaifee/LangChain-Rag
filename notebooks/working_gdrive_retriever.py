"""
Working Google Drive PDF Retriever using Direct API
This bypasses the LangChain GoogleDriveRetriever issues
"""
from dotenv import load_dotenv
load_dotenv()

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from langchain_core.documents import Document
import io
import os

class WorkingGoogleDriveRetriever:
    """Custom Google Drive retriever that actually works"""
    
    def __init__(self, folder_id="root", num_results=10, token_path="../token.json"):
        self.folder_id = folder_id
        self.num_results = num_results
        
        # Authenticate
        creds = Credentials.from_authorized_user_file(token_path)
        self.service = build('drive', 'v3', credentials=creds)
    
    def _list_files(self, query=None):
        """List files in the folder"""
        # Build the query
        q = f"'{self.folder_id}' in parents and trashed=false"
        if query:
            q += f" and fullText contains '{query}'"
        
        results = self.service.files().list(
            q=q,
            pageSize=self.num_results,
            fields="files(id, name, mimeType, webViewLink)"
        ).execute()
        
        return results.get('files', [])
    
    def _download_file(self, file_id, mime_type):
        """Download file content"""
        try:
            if mime_type == 'application/pdf':
                # Download PDF directly
                request = self.service.files().get_media(fileId=file_id)
                file_content = io.BytesIO()
                downloader = MediaIoBaseDownload(file_content, request)
                
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                
                file_content.seek(0)
                return file_content.read()
            
            elif mime_type == 'text/plain':
                # Download text file
                request = self.service.files().get_media(fileId=file_id)
                content = request.execute()
                return content.decode('utf-8')
            
            elif mime_type == 'application/vnd.google-apps.document':
                # Export Google Doc as plain text
                request = self.service.files().export_media(
                    fileId=file_id,
                    mimeType='text/plain'
                )
                content = request.execute()
                return content.decode('utf-8')
            
            else:
                return None
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None
    
    def _extract_text_from_pdf(self, pdf_bytes):
        """Extract text from PDF bytes"""
        try:
            from pypdf import PdfReader
            import io
            
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
    
    def invoke(self, query=""):
        """Retrieve documents from Google Drive"""
        files = self._list_files(query if query else None)
        documents = []
        
        print(f"Found {len(files)} files")
        
        for file in files:
            print(f"Processing: {file['name']}...")
            
            content = self._download_file(file['id'], file['mimeType'])
            
            if content is None:
                print(f"  ⚠️  Skipped (unsupported type: {file['mimeType']})")
                continue
            
            # Extract text from PDF if needed
            if file['mimeType'] == 'application/pdf':
                if isinstance(content, bytes):
                    text = self._extract_text_from_pdf(content)
                else:
                    text = content
            else:
                text = content if isinstance(content, str) else content.decode('utf-8')
            
            # Create LangChain Document
            doc = Document(
                page_content=text,
                metadata={
                    'title': file['name'],
                    'source': file.get('webViewLink', ''),
                    'mime_type': file['mimeType'],
                    'file_id': file['id']
                }
            )
            
            documents.append(doc)
            print(f"  ✅ Loaded ({len(text)} chars)")
        
        return documents


# Example usage
if __name__ == "__main__":
    folder_id = "1x_vHYamawB-f2aVdZbzSjVO0gbAqI_l7"
    
    retriever = WorkingGoogleDriveRetriever(
        folder_id=folder_id,
        num_results=10
    )
    
    # Retrieve all documents
    print("=" * 60)
    print("Retrieving all documents from folder...")
    print("=" * 60)
    docs = retriever.invoke("")
    
    print(f"\n✅ Successfully retrieved {len(docs)} documents!\n")
    
    for i, doc in enumerate(docs, 1):
        print("-" * 60)
        print(f"Document {i}:")
        print(f"  Title: {doc.metadata.get('title')}")
        print(f"  Source: {doc.metadata.get('source')}")
        print(f"  Type: {doc.metadata.get('mime_type')}")
        print(f"  Content length: {len(doc.page_content)} characters")
        print(f"  Content preview: {doc.page_content[:200]}...")
