import re
from io import BytesIO
from typing import Dict, List

import pypdf


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def estimate_tokens(text: str) -> int:
    return len(text) // 4


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    if not text:
        return []

    char_chunk_size = chunk_size * 4
    char_overlap = overlap * 4

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + char_chunk_size

        if end < text_length:
            sentence_end = max(
                text.rfind(".", start, end),
                text.rfind("!", start, end),
                text.rfind("?", start, end),
                text.rfind("\n", start, end),
            )

            if sentence_end > start + char_chunk_size // 2:
                end = sentence_end + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - char_overlap
        if start >= text_length:
            break

    return chunks


def load_pdf(file_content: bytes, filename: str) -> str:
    try:
        pdf_file = BytesIO(file_content)
        reader = pypdf.PdfReader(pdf_file)
        text_parts = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

        full_text = "\n\n".join(text_parts)
        return clean_text(full_text)
    except Exception as e:
        raise ValueError(f"Error loading PDF {filename}: {str(e)}")


def load_text_file(file_content: bytes, filename: str) -> str:
    try:
        try:
            text = file_content.decode("utf-8")
        except UnicodeDecodeError:
            text = file_content.decode("latin-1")

        return clean_text(text)
    except Exception as e:
        raise ValueError(f"Error loading text file {filename}: {str(e)}")


def process_documents(uploaded_files: List, user_id: str = None) -> List[Dict]:
    all_chunks = []

    for uploaded_file in uploaded_files:
        file_content = uploaded_file.read()
        filename = uploaded_file.name
        file_extension = filename.split(".")[-1].lower()

        if file_extension == "pdf":
            text = load_pdf(file_content, filename)
        elif file_extension in ["txt", "md"]:
            text = load_text_file(file_content, filename)
        else:
            continue

        if not text:
            continue

        chunks = chunk_text(text, chunk_size=800, overlap=150)

        for idx, chunk in enumerate(chunks):
            chunk_dict = {
                "id": f"{filename.replace(' ', '_')}_chunk_{idx}",
                "text": chunk,
                "source": filename,
                "chunk_index": idx,
            }
            if user_id:
                chunk_dict["user_id"] = user_id

            all_chunks.append(chunk_dict)

    return all_chunks
