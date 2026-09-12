import os
import glob
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class CustomEnsembleRetriever:
    """A bulletproof Reciprocal Rank Fusion (RRF) retriever."""
    def __init__(self, bm25_retriever, dense_retriever):
        self.bm25_retriever = bm25_retriever
        self.dense_retriever = dense_retriever

    def invoke(self, query: str) -> List[Document]:
        bm25_docs = self.bm25_retriever.invoke(query)
        dense_docs = self.dense_retriever.invoke(query)
        
        fused_scores = {}
        doc_map = {}
        
        for weight, docs in zip([0.4, 0.6], [bm25_docs, dense_docs]):
            for rank, doc in enumerate(docs):
                content = doc.page_content
                if content not in fused_scores:
                    fused_scores[content] = 0.0
                    doc_map[content] = doc
                fused_scores[content] += weight * (1 / (rank + 60))
                
        sorted_docs = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        return [doc_map[content] for content, _ in sorted_docs[:30]]


def load_corpus_documents(corpus_dir: str = "./corpus") -> List[Document]:
    raw_docs: List[Document] = []
    
    # 1. Load Markdown & Text files
    for filepath in glob.glob(f"{corpus_dir}/*.md") + glob.glob(f"{corpus_dir}/*.txt"):
        filename = os.path.basename(filepath)
        loader = TextLoader(filepath, encoding="utf-8")
        docs = loader.load()
        for d in docs:
            d.metadata["source"] = filename
        raw_docs.extend(docs)

    # 2. Load PDF files with PyMuPDF
    for filepath in glob.glob(f"{corpus_dir}/*.pdf"):
        filename = os.path.basename(filepath)
        loader = PyMuPDFLoader(filepath)
        pdf_pages = loader.load()
        for p in pdf_pages:
            p.metadata["source"] = filename
            p.metadata["page"] = p.metadata.get("page", 0) + 1
        raw_docs.extend(pdf_pages)

    if not raw_docs:
        raise ValueError(f"No documents found in '{corpus_dir}'.")
    
    return raw_docs


def build_hybrid_retriever(corpus_dir: str = "./corpus") -> CustomEnsembleRetriever:
    raw_docs = load_corpus_documents(corpus_dir)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " "]
    )
    split_docs = splitter.split_documents(raw_docs)

    # Keyword Search (BM25)
    bm25_retriever = BM25Retriever.from_documents(split_docs)
    bm25_retriever.k = 30

    # Semantic Search (Gemini Embeddings)
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    vectorstore = InMemoryVectorStore.from_documents(split_docs, embeddings)
    dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 30})

    # Hybrid Ensemble (Custom RRF)
    return CustomEnsembleRetriever(
        bm25_retriever=bm25_retriever,
        dense_retriever=dense_retriever
    )