import os
import logging
from backend.config import settings

logger = logging.getLogger(__name__)

# Basic financial knowledge base focused on Indian context and personal finance
FINANCIAL_KNOWLEDGE = [
    "PPF (Public Provident Fund) is a long-term, tax-saving investment in India with a 15-year lock-in period. Both the investment and the interest earned are tax-free under Section 80C.",
    "ELSS (Equity Linked Savings Scheme) is a mutual fund category that offers tax benefits under Section 80C. It has the shortest lock-in period of 3 years among all tax-saving options.",
    "An emergency fund should typically cover 3 to 6 months of your essential living expenses. It should be kept in a highly liquid asset like a savings account or liquid mutual fund.",
    "The 50/30/20 budgeting rule suggests allocating 50% of your income to needs, 30% to wants, and 20% to savings and investments.",
    "A high portfolio risk score (e.g., above 7/10) indicates heavy allocation in volatile assets like direct Equity or Crypto. It is suitable for long-term horizons.",
    "SIP (Systematic Investment Plan) allows you to invest a fixed amount regularly in mutual funds, benefiting from rupee cost averaging and compounding.",
    "Term life insurance provides high coverage for a low premium. It is the purest form of life insurance but returns no maturity value if you survive the term.",
    "Health insurance is essential to protect your savings from medical emergencies. Premiums paid offer tax deductions under Section 80D."
]

def get_vector_store():
    """Initialize and return the Chroma vector store using Mistral embeddings."""
    if not settings.MISTRAL_API_KEY:
        return None
    try:
        from langchain_chroma import Chroma
        from langchain_mistralai import MistralAIEmbeddings

        embeddings = MistralAIEmbeddings(
            model="mistral-embed",
            api_key=settings.MISTRAL_API_KEY,
        )
        persist_directory = settings.CHROMA_PERSIST_DIR

        # Check if directory exists and has files
        is_empty = not os.path.exists(persist_directory) or len(os.listdir(persist_directory)) == 0

        vector_store = Chroma(
            collection_name="financial_knowledge",
            embedding_function=embeddings,
            persist_directory=persist_directory
        )

        if is_empty:
            logger.info("Initializing ChromaDB with financial knowledge base...")
            vector_store.add_texts(texts=FINANCIAL_KNOWLEDGE)

        return vector_store
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB: {e}")
        return None

def search_knowledge_base(query: str, k: int = 2) -> str:
    """Search the vector database for relevant financial knowledge.

    Returns a formatted string of the retrieved knowledge chunks.
    """
    vector_store = get_vector_store()
    if not vector_store:
        return ""

    try:
        docs = vector_store.similarity_search(query, k=k)
        if docs:
            return "\n".join([f"- {doc.page_content}" for doc in docs])
        return ""
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return ""
