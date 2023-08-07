from typing import Union
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from pathlib import Path
import shutil, zipfile, uuid

from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import Chroma
from sentence_transformers import SentenceTransformer
import chromadb
from typing import List


app = FastAPI()

class MiniLMEmbeddings(Embeddings):
    def __init__(self):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.encoder.encode(texts).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents(text)

class DBQuery(BaseModel):
    query: str

COLLECTION_NAME = "obsidian" # TODO: use env vars
NUM_RESULTS=10 # 10 nearest neighbors
db_client = chromadb.HttpClient(host='localhost', port=8080)

# DEFINE APPLICATION ROUTES

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/api/reindex/")
async def upload_directory(directory: UploadFile = File(...)):
    # clear db and uploads folder
    db_client.reset()
    collection = db_client.get_or_create_collection(COLLECTION_NAME)

    uploads_dir = Path('./uploads')
    if uploads_dir.exists() and uploads_dir.is_dir():
        for p in uploads_dir.iterdir():
            if p.is_file(): p.unlink()
            elif p.is_dir(): shutil.rmtree(p)

    # save and decompress new uploads
    decompressed_path = Path('./uploads/decompressed') 
    decompressed_path.mkdir(parents=True, exist_ok=True)

    with uploads_dir.joinpath(directory.filename).open("wb") as buffer:
        while content := await directory.read(1024): 
            buffer.write(content)

    with zipfile.ZipFile(f'./uploads/{directory.filename}', 'r') as zip_file:
        zip_file.extractall('./uploads/decompressed')

    # populate db
    raw_documents = DirectoryLoader(path='./uploads/decompressed', glob="**/*.md", use_multithreading=True).load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = text_splitter.split_documents(raw_documents)

    collection.add(
        ids=[str(uuid.uuid1()) for _ in documents],
        metadatas=[ doc.metadata for doc in documents ],
        documents=[ doc.page_content for doc in documents ],
        embeddings=MiniLMEmbeddings().embed_documents([ doc.page_content for doc in documents ])
    )

    return { "message": "reindexed successfully" }

@app.post("/api/query/")
async def query(q: DBQuery):
    collection = db_client.get_or_create_collection(COLLECTION_NAME)

    docs = collection.query(
            query_embeddings=MiniLMEmbeddings().embed_query(q.query),
            n_results=NUM_RESULTS
        )

    return { "message": docs }

