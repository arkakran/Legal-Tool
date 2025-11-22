import time
import os
from loguru import logger

from app.services.pdf_processor import PDFProcessor
from app.services.metadata_extractor import MetadataExtractor
from app.services.vector_store import VectorStore
from app.services.llm_analyzer import LLMAnalyzer
from app.services.post_processor import PostProcessor
from app.utils.embeddings import EmbeddingService
from app.utils.helpers import calculate_content_hash


class AnalysisPipeline:
    """Main pipeline for legal brief analysis."""

    def __init__(self, settings):
        self.settings = settings
        logger.info("Initializing analysis pipeline...")

        self.embedding_service = EmbeddingService(
            model_name=settings.EMBEDDING_MODEL,
            device=settings.EMBEDDING_DEVICE
        )

        self.pdf_processor = PDFProcessor(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

        self.metadata_extractor = MetadataExtractor()

        self.vector_store = VectorStore(
            embedding_service=self.embedding_service,
            m=settings.FAISS_M,
            ef_construction=settings.FAISS_EF_CONSTRUCTION
        )

        self.llm_analyzer = LLMAnalyzer(
            api_key=settings.GROQ_API_KEY,
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE
        )

        self.post_processor = PostProcessor(
            top_k=settings.FINAL_OUTPUT_COUNT
        )

        logger.info("Pipeline initialized")

    def analyze_document(self, pdf_path: str, filename: str) -> dict:
        """Run complete analysis pipeline."""

        start_time = time.time()

        try:
            # Step 1: Validate file path
            logger.info("Step 1: Validating and hashing file...")

            if not os.path.isfile(pdf_path):
                logger.error(f"PDF not found: {pdf_path}")
                raise FileNotFoundError("Uploaded PDF not found on server.")

            with open(pdf_path, "rb") as f:
                content = f.read()

            if not content:
                raise ValueError("Empty PDF file.")

            doc_id = calculate_content_hash(content)
            logger.info(f"Document ID: {doc_id[:12]}...")

            # Step 2: Process PDF
            logger.info("Step 2: Processing PDF...")
            chunks, total_pages = self.pdf_processor.process_pdf(pdf_path, doc_id)

            if not chunks:
                raise ValueError("No text extracted from PDF.")

            # Step 3: Extract metadata
            logger.info("Step 3: Extracting metadata...")
            metadata = self.metadata_extractor.extract_metadata(chunks, filename)

            # Step 4: Initialize vector store
            logger.info("Step 4: Initializing vector store...")
            self.vector_store.initialize_index(doc_id, force_new=True)

            # Step 5: Add chunks
            logger.info("Step 5: Embedding & indexing...")
            self.vector_store.add_chunks(chunks)

            # Step 6: Retrieve relevant chunks
            logger.info("Step 6: Retrieving relevant chunks...")
            query = "Extract key legal arguments from this document"
            retrieved_chunks = self.vector_store.search(
                query=query,
                top_k=self.settings.TOP_K_RETRIEVAL,
                ef_search=self.settings.FAISS_EF_SEARCH
            )

            # Step 7: LLM analysis
            logger.info("Step 7: Analyzing with LLM...")
            llm_output = self.llm_analyzer.analyze_chunks(
                chunks_with_scores=retrieved_chunks,
                max_chunks=30
            )

            # Step 8: Post-processing
            logger.info("Step 8: Post-processing...")
            final_points = self.post_processor.process_and_rank(
                extracted_points=llm_output.extracted_points,
                chunks=chunks
            )

            processing_time = time.time() - start_time

            result = {
                "document_id": doc_id,
                "document_name": filename,
                "total_pages": total_pages,
                "total_chunks": len(chunks),
                "key_points": [p.model_dump() for p in final_points],
                "processing_time": round(processing_time, 2),
                "metadata": metadata
            }

            logger.info(f"Analysis complete in {processing_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
