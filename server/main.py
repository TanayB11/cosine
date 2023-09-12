from typing import Union
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import shutil, zipfile, uuid

from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import LanceDB
from sentence_transformers import SentenceTransformer
import lancedb
from typing import List


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MiniLMEmbeddings(Embeddings):
    def __init__(self):
        self.encoder = SentenceTransformer('msmarco-distilroberta-base-v2')

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.encoder.encode(texts).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents(text)

class DBQuery(BaseModel):
    query: str

TABLE_NAME = "obsidian" # TODO: use env vars
NUM_RESULTS=10 # 10 nearest neighbors
db_client = lancedb.connect('./lancedb')
embeddings = MiniLMEmbeddings()

# DEFINE APPLICATION ROUTES

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/api/reindex/")
async def upload_directory(directory: UploadFile = File(...)):
    # clear db and uploads folder
    db_client.drop_database()

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

    table = db_client.create_table(
            TABLE_NAME,
            data=[
                {
                    "id": str(uuid.uuid1()),
                    "metadata": doc.metadata['source'],
                    "text": doc.page_content,
                    "vector": embeddings.embed_query(doc.page_content),
                } for doc in documents
            ],
        )

    return { "message": "reindexed successfully" }

@app.post("/api/query/")
async def query(q: DBQuery):
    collection = db_client.open_table(TABLE_NAME)
    docs = collection.search(embeddings.embed_query(q.query)).to_df()
    docs = docs[['metadata', 'text']].to_dict()

    docs['metadata'] = list(docs['metadata'].values())
    docs['text'] = list(docs['text'].values())

    return { "message" : docs }

