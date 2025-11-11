import os
import openai
import json
import config
import chromadb
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

# ----------------------------------------------------------
# SETUP EMBEDDING MODEL + CHROMA CLIENT
# ----------------------------------------------------------
embedder = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./gdpr_chroma")
collection = chroma_client.get_or_create_collection("gdpr_hr")

# ----------------------------------------------------------
# UTILITY FUNCTIONS
# ----------------------------------------------------------
def extract_text_from_pdf(file_path):
    """Extract text from a PDF file"""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def chunk_text(text, chunk_size=800):
    """Split long text into smaller chunks for embedding"""
    words = text.split()
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks


def embed_and_store_documents(pdf_files):
    """Embed and store text chunks into Chroma DB"""
    print("📘 Indexing GDPR documents...")
    for pdf_file in pdf_files:
        if not os.path.exists(pdf_file):
            print(f"⚠️  Skipping {pdf_file} - file not found")
            continue
        text = extract_text_from_pdf(pdf_file)
        chunks = chunk_text(text)
        embeddings = embedder.encode(chunks).tolist()
        ids = [f"{os.path.basename(pdf_file)}_{i}" for i in range(len(chunks))]
        collection.add(documents=chunks, embeddings=embeddings, ids=ids)
    print("✅ Documents indexed successfully!")


# Run only once - index documents if collection is empty
if len(collection.get()["ids"]) == 0:
    # Try to find GDPR documents
    gdpr_files = []
    possible_paths = [
        "gdpr_documents/Art.pdf",
        "gdpr_documents/CELEX_32016R0679_EN_TXT.pdf",
        "Art.pdf",
        "CELEX_32016R0679_EN_TXT.pdf"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            gdpr_files.append(path)
    
    if gdpr_files:
        embed_and_store_documents(gdpr_files)
    else:
        print("⚠️  No GDPR documents found. Place PDF files in root or gdpr_documents/ folder")


# ----------------------------------------------------------
# MAIN GDPR CHATBOT SERVICE
# ----------------------------------------------------------
class GDPRChatbotService:
    """GDPR & AI in HR Chatbot using OpenAI and Chroma DB"""

    def __init__(self):
        openai.api_key = config.OPENAI_API_KEY
        self.model = "gpt-3.5-turbo"

    def _retrieve_context(self, query, top_k=3):
        """Retrieve relevant chunks from Chroma DB"""
        query_embedding = embedder.encode([query]).tolist()[0]
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
        return "\n\n".join(results["documents"][0])

    def ask_question(self, question):
        """Answer a GDPR/AI in HR related question"""
        try:
            context = self._retrieve_context(question)
            prompt = f"""
You are a GDPR compliance expert focused on HR applications and AI ethics.
Base your answer ONLY on the official GDPR (EU 2016/679) and the 2025 HR-AI guide provided.

Context from documents:
{context}

Question:
{question}

Provide a clear, concise, and compliant answer.
Always cite relevant GDPR Articles and explain in simple language.
"""

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a GDPR compliance assistant for AI systems in HR."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=800
            )

            answer = response["choices"][0]["message"]["content"]
            return {"question": question, "answer": answer}

        except Exception as e:
            return {"error": str(e), "question": question}