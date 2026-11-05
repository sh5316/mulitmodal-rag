"""다중 벡터 검색기(Multi-Vector Retriever) 모듈.

요약본은 벡터스토어에 임베딩해 검색에 사용하고,
원본(텍스트/표/이미지)은 docstore에 저장해 반환합니다.
"""

from __future__ import annotations

import uuid


def build_multi_vector_retriever(
    texts: list[str],
    text_summaries: list[str],
    tables: list[str],
    table_summaries: list[str],
    image_b64: list[str],
    image_summaries: list[str],
    collection_name: str = "multimodal_rag",
):
    """요약본으로 검색하고 원본을 반환하는 다중 벡터 검색기를 만든다."""
    from langchain.retrievers.multi_vector import MultiVectorRetriever
    from langchain.storage import InMemoryStore
    from langchain_chroma import Chroma
    from langchain_core.documents import Document
    from langchain_openai import OpenAIEmbeddings

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=OpenAIEmbeddings(),
    )
    store = InMemoryStore()
    id_key = "doc_id"

    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=store,
        id_key=id_key,
    )

    def _add(contents: list[str], summaries: list[str]):
        if not summaries:
            return
        ids = [str(uuid.uuid4()) for _ in contents]
        summary_docs = [
            Document(page_content=s, metadata={id_key: ids[i]})
            for i, s in enumerate(summaries)
        ]
        retriever.vectorstore.add_documents(summary_docs)
        retriever.docstore.mset(list(zip(ids, contents)))

    _add(texts, text_summaries)
    _add(tables, table_summaries)
    _add(image_b64, image_summaries)

    return retriever
