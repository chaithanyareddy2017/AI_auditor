import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "data", "auditor.db")

def index_resume(pdf_path, user_email):
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection_name = f"resume_{user_email.replace('@','_').replace('.','_')}"
    
    try:
        client.delete_collection(collection_name)
    except:
        pass
    
    collection = client.get_or_create_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    documents = SimpleDirectoryReader(input_files=[pdf_path]).load_data()
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    return index

def query_resume(user_email, query="summarize skills and experience"):
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection_name = f"resume_{user_email.replace('@','_').replace('.','_')}"
    
    try:
        collection = client.get_or_create_collection(collection_name)
        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
        query_engine = index.as_query_engine()
        response = query_engine.query(query)
        return str(response)
    except Exception as e:
        return ""