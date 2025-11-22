from typing import List, Dict, Any
import pdfplumber
from loguru import logger


class PDFProcessor:
    def __init__(self, chunk_size: int = 1500, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_pdf(self, pdf_path: str, doc_id: str) -> tuple[List[Dict[str, Any]], int]:
        chunks = []
        total_pages = 0

        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"Processing PDF: {total_pages} pages")

                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()

                    if text and text.strip():
                        # Split page text into chunks while preserving page number
                        page_chunks = self._split_text_with_page(
                            text=text,
                            page_number=page_num,
                            doc_id=doc_id,
                            total_pages=total_pages
                        )
                        chunks.extend(page_chunks)

            logger.info(f"Processed {total_pages} pages into {len(chunks)} chunks")
            return chunks, total_pages

        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            raise RuntimeError(f"Failed to process PDF: {e}") from e

    def _split_text_with_page(self, text: str, page_number: int, doc_id: str, total_pages: int) -> List[Dict[str, Any]]:
        chunks = []

        # Simple splitting by character count with overlap
        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            if chunk_text.strip():
                chunk = {
                    'text': chunk_text.strip(),
                    'metadata': {
                        'chunk_id': f"{doc_id}_page{page_number}_chunk{chunk_index}",
                        'page_number': page_number,
                        'document_id': doc_id,
                        'total_pages': total_pages,
                        'chunk_index': chunk_index
                    }
                }
                chunks.append(chunk)
                chunk_index += 1

            # Move start with overlap
            start = end - self.chunk_overlap if end < len(text) else end

        return chunks
