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
import fitz

from app.core.config import settings

ENDPOINT   = settings.AZURE_SEARCH_ENDPOINT
ADMIN_KEY  = settings.AZURE_SEARCH_ADMIN_KEY
INDEX_NAME = settings.AZURE_SEARCH_INDEX_EXTERNAL
OAI_ENDPOINT = settings.AZURE_OPENAI_ENDPOINT
OAI_KEY      = settings.AZURE_OPENAI_API_KEY
OAI_VERSION  = settings.AZURE_OPENAI_API_VERSION
EMBED_MODEL  = settings.AZURE_OPENAI_DEPLOYMENT_EMBED

print("=== OC AI Copilot — External Product Docs Ingestion ===")
print(f"Search endpoint : {ENDPOINT}")
print(f"Index name      : {INDEX_NAME}")
print("")

# Step 1: Create external index
print("Step 1: Creating external search index...")

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
    SimpleField(name="product_line",   type=SearchFieldDataType.String, filterable=True, retrievable=True),
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

# Step 2: Ingest documents
print("")
print("Step 2: Ingesting external product documents...")

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
        "file": "sample_docs/external/Duration-Premium-Shingles-Spec.pdf",
        "name": "Duration Premium Shingles — Product Specification Sheet",
        "version": "Rev 9",
        "approved_date": "2025-02-01",
        "product_line": "roofing",
        "stream_type": "external"
    },
    {
        "file": "sample_docs/external/EcoTouch-PINK-FIBERGLAS-Spec.pdf",
        "name": "EcoTouch PINK FIBERGLAS Insulation — Product Data Sheet",
        "version": "Rev 14",
        "approved_date": "2025-01-15",
        "product_line": "insulation",
        "stream_type": "external"
    },
    {
        "file": "sample_docs/external/Thermafiber-Mineral-Wool-Fire-Rating.pdf",
        "name": "Thermafiber Mineral Wool — Fire Rating and Technical Specification",
        "version": "Rev 8",
        "approved_date": "2025-01-10",
        "product_line": "insulation",
        "stream_type": "external"
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
    print(f"    {len(chunks)} chunks created")

    documents = []
    for i, chunk_text_val in enumerate(chunks):
        print(f"    Embedding chunk {i+1}/{len(chunks)}...")
        vector = get_embedding(chunk_text_val)
        doc_id = doc_meta["product_line"] + "_" + str(i)
        documents.append({
            "chunk_id":       doc_id + "_" + str(i),
            "document_id":    doc_meta["product_line"],
            "document_name":  doc_meta["name"],
            "content":        chunk_text_val,
            "content_vector": vector,
            "section":        "Chunk " + str(i+1),
            "version":        doc_meta["version"],
            "approved_date":  doc_meta["approved_date"],
            "product_line":   doc_meta["product_line"],
            "site":           "All Regions",
            "stream_type":    doc_meta["stream_type"],
        })

    search_client.upload_documents(documents=documents)
    print(f"    Uploaded {len(documents)} chunks")
    total_chunks += len(documents)

print("")
print("=== External ingestion complete! ===")
print(f"Total chunks indexed: {total_chunks}")
print(f"Index: {INDEX_NAME}")
print("")
print("Ready to test at http://localhost:3002/customer")
print("Try asking:")
print("  What is the wind resistance rating for Duration Premium shingles?")
print("  What R-value do I need for a 2x6 wall in Climate Zone 5?")
print("  What fire rating does Thermafiber mineral wool carry?")
