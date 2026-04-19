import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType,
    SimpleField, SearchableField, VectorSearch,
    HnswAlgorithmConfiguration, VectorSearchProfile,
    SemanticConfiguration, SemanticSearch, SemanticPrioritizedFields,
    SemanticField
)
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
import fitz  # pymupdf

# Load settings
from app.core.config import settings

ENDPOINT   = settings.AZURE_SEARCH_ENDPOINT
ADMIN_KEY  = settings.AZURE_SEARCH_ADMIN_KEY
INDEX_NAME = settings.AZURE_SEARCH_INDEX_INTERNAL
OAI_ENDPOINT = settings.AZURE_OPENAI_ENDPOINT
OAI_KEY      = settings.AZURE_OPENAI_API_KEY
OAI_VERSION  = settings.AZURE_OPENAI_API_VERSION
EMBED_MODEL  = settings.AZURE_OPENAI_DEPLOYMENT_EMBED

print("=== OC AI Copilot — Document Ingestion ===")
print(f"Search endpoint : {ENDPOINT}")
print(f"Index name      : {INDEX_NAME}")
print(f"Embed model     : {EMBED_MODEL}")
print("")

# ── Step 1: Create the index ────────────────────────────────────────────────
print("Step 1: Creating search index...")

index_client = SearchIndexClient(
    endpoint=ENDPOINT,
    credential=AzureKeyCredential(ADMIN_KEY)
)

fields = [
    SimpleField(name="chunk_id",       type=SearchFieldDataType.String, key=True),
    SimpleField(name="document_id",    type=SearchFieldDataType.String, filterable=True),
    SearchableField(name="document_name", type=SearchFieldDataType.String, retrievable=True),
    SearchableField(name="content",    type=SearchFieldDataType.String, retrievable=True),
    SimpleField(name="section",        type=SearchFieldDataType.String, retrievable=True),
    SimpleField(name="version",        type=SearchFieldDataType.String, retrievable=True),
    SimpleField(name="approved_date",  type=SearchFieldDataType.String, retrievable=True),
    SimpleField(name="domain",         type=SearchFieldDataType.String, filterable=True, retrievable=True),
    SimpleField(name="site",           type=SearchFieldDataType.String, filterable=True, retrievable=True),
    SimpleField(name="stream_type",    type=SearchFieldDataType.String, filterable=True, retrievable=True),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=3072,
        vector_search_profile_name="oc-hnsw-profile"
    ),
]

vector_search = VectorSearch(
    algorithms=[HnswAlgorithmConfiguration(name="oc-hnsw")],
    profiles=[VectorSearchProfile(name="oc-hnsw-profile", algorithm_configuration_name="oc-hnsw")]
)

semantic_config = SemanticConfiguration(
    name="oc-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        content_fields=[SemanticField(field_name="content")],
        keywords_fields=[SemanticField(field_name="document_name")]
    )
)

index = SearchIndex(
    name=INDEX_NAME,
    fields=fields,
    vector_search=vector_search,
    semantic_search=SemanticSearch(configurations=[semantic_config])
)

try:
    index_client.delete_index(INDEX_NAME)
    print(f"  Deleted existing index: {INDEX_NAME}")
except:
    pass

index_client.create_index(index)
print(f"  Index created: {INDEX_NAME}")

# ── Step 2: Embed and ingest documents ─────────────────────────────────────
print("")
print("Step 2: Ingesting documents...")

oai_client = AzureOpenAI(
    azure_endpoint=OAI_ENDPOINT,
    api_key=OAI_KEY,
    api_version=OAI_VERSION
)

search_client = SearchClient(
    endpoint=ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(ADMIN_KEY)
)

DOCS = [
    {
        "file": "sample_docs/EHS-LOTO-003-SC.pdf",
        "name": "EHS-LOTO-003 — LOTO Procedure SC Doors Assembly Line",
        "version": "Rev 4",
        "approved_date": "2025-03-01",
        "domain": "safety",
        "site": "Aiken SC",
        "stream_type": "internal"
    },
    {
        "file": "sample_docs/OC-HR-ONBOARD-ENG-003.pdf",
        "name": "OC-HR-ONBOARD-ENG-003 — New Automation Engineer Onboarding Guide",
        "version": "Rev 2",
        "approved_date": "2025-01-15",
        "domain": "new_hire",
        "site": "All Sites",
        "stream_type": "internal"
    },
    {
        "file": "sample_docs/OC-MAINT-PM-004.pdf",
        "name": "OC-MAINT-PM-004 — Injection Molding Machine PM Schedule",
        "version": "Rev 4",
        "approved_date": "2025-02-01",
        "domain": "maintenance",
        "site": "All Sites",
        "stream_type": "internal"
    },
]

def chunk_text(text, chunk_size=400, overlap=80):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        if len(chunk.strip()) > 30:
            chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def get_embedding(text):
    resp = oai_client.embeddings.create(
        input=text[:8000],
        model=EMBED_MODEL
    )
    return resp.data[0].embedding

total_chunks = 0
for doc_meta in DOCS:
    print(f"  Processing: {doc_meta['name']}")
    pdf = fitz.open(doc_meta["file"])
    full_text = ""
    for page in pdf:
        full_text += page.get_text() + " "
    pdf.close()

    chunks = chunk_text(full_text)
    print(f"    Pages extracted, {len(chunks)} chunks created")

    documents = []
    for i, chunk_text_val in enumerate(chunks):
        print(f"    Embedding chunk {i+1}/{len(chunks)}...")
        vector = get_embedding(chunk_text_val)
        documents.append({
            "chunk_id":      f"{doc_meta['domain']}_{i:04d}_{i}",
            "document_id":   doc_meta["domain"],
            "document_name": doc_meta["name"],
            "content":       chunk_text_val,
            "content_vector": vector,
            "section":       f"Chunk {i+1}",
            "version":       doc_meta["version"],
            "approved_date": doc_meta["approved_date"],
            "domain":        doc_meta["domain"],
            "site":          doc_meta["site"],
            "stream_type":   doc_meta["stream_type"],
        })

    result = search_client.upload_documents(documents=documents)
    print(f"    Uploaded {len(documents)} chunks to index")
    total_chunks += len(documents)

print("")
print(f"=== Ingestion complete! ===")
print(f"Total chunks indexed: {total_chunks}")
print(f"Index: {INDEX_NAME}")
print("")
print("Ready to test — restart uvicorn and ask:")
print("  LOTO procedure for SC Doors assembly line")
print("  New hire onboarding for automation engineer")
print("  Injection molding PM schedule")
