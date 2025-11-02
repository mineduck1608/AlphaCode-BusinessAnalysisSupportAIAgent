# Chroma wrapper + embedder (Gemini embeddings)
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# load .env if present
load_dotenv()

try:
	import chromadb
	from chromadb.config import Settings
except Exception:
	chromadb = None

import google.generativeai as genai

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-004")

if GENAI_API_KEY:
	genai.configure(api_key=GENAI_API_KEY)


class VectorStore:
	def __init__(self, persist_directory: str = None):
		if chromadb is None:
			raise RuntimeError("chromadb not installed")
		settings = Settings(persist_directory=persist_directory) if persist_directory else Settings()
		self.client = chromadb.Client(settings)
		self.collection = self.client.get_or_create_collection("requirements")

	def embed(self, texts: List[str]) -> List[List[float]]:
		# Use Gemini embedding API via google.generativeai
		resp = genai.embeddings.create(model=EMBED_MODEL, input=texts)
		# response shape varies; adapt accordingly
		embeddings = [item.embedding for item in resp.data]
		return embeddings

	def upsert(self, ids: List[str], texts: List[str], metadatas: List[Dict[str, Any]]):
		embs = self.embed(texts)
		self.collection.upsert(
			ids=ids,
			metadatas=metadatas,
			documents=texts,
			embeddings=embs,
		)

	def query(self, query_text: str, n_results: int = 5):
		qemb = self.embed([query_text])[0]
		res = self.collection.query(query_embeddings=[qemb], n_results=n_results, include=['documents','metadatas','distances'])
		return res
# CRUD + query to Chroma