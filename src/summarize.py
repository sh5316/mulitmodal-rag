"""요약 체인 모듈.

텍스트/표는 LLM으로, 이미지는 비전 모델로 요약합니다.
요약본은 검색(retrieval) 품질을 높이는 데 사용됩니다.
"""

from __future__ import annotations

import base64
from pathlib import Path


def summarize_texts(texts: list[str], model: str = "gpt-4o-mini") -> list[str]:
    """텍스트/표 요소를 요약한다."""
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI

    prompt = ChatPromptTemplate.from_template(
        "다음 내용을 검색에 최적화된 형태로 간결하게 요약하세요.\n\n{element}"
    )
    chain = prompt | ChatOpenAI(model=model, temperature=0) | StrOutputParser()
    return chain.batch(texts, {"max_concurrency": 5})


def encode_image(image_path: str | Path) -> str:
    """이미지를 base64 문자열로 인코딩한다."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def summarize_image(image_path: str | Path, model: str = "gpt-4o") -> str:
    """단일 이미지를 비전 모델로 요약한다."""
    from langchain_core.messages import HumanMessage
    from langchain_openai import ChatOpenAI

    b64 = encode_image(image_path)
    chat = ChatOpenAI(model=model, temperature=0, max_tokens=1024)
    msg = chat.invoke(
        [
            HumanMessage(
                content=[
                    {"type": "text", "text": "이 이미지를 검색용으로 자세히 설명하세요."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                ]
            )
        ]
    )
    return msg.content


def summarize_images(figures_dir: str | Path = "data/figures") -> tuple[list[str], list[str]]:
    """디렉토리 내 모든 이미지를 요약한다.

    Returns:
        (base64 이미지 리스트, 요약 리스트) 튜플.
    """
    figures_dir = Path(figures_dir)
    img_b64, summaries = [], []
    for img_path in sorted(figures_dir.glob("*.jpg")):
        img_b64.append(encode_image(img_path))
        summaries.append(summarize_image(img_path))
    return img_b64, summaries
