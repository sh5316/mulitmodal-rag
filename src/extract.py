"""PDF 파싱 모듈.

PDF에서 텍스트, 표, 이미지(figure)를 분리 추출합니다.
unstructured 라이브러리를 사용한 구현 예시입니다.
"""

from __future__ import annotations

from pathlib import Path


def extract_pdf_elements(
    pdf_path: str | Path,
    figures_dir: str | Path = "data/figures",
):
    """PDF를 파싱해 텍스트/표/이미지 요소로 분리한다.

    Args:
        pdf_path: 원본 PDF 경로.
        figures_dir: 추출한 이미지를 저장할 디렉토리.

    Returns:
        unstructured 요소들의 리스트.
    """
    from unstructured.partition.pdf import partition_pdf

    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    elements = partition_pdf(
        filename=str(pdf_path),
        extract_images_in_pdf=True,
        infer_table_structure=True,
        chunking_strategy="by_title",
        max_characters=4000,
        new_after_n_chars=3800,
        combine_text_under_n_chars=2000,
        extract_image_block_output_dir=str(figures_dir),
    )
    return elements


def categorize_elements(elements):
    """요소들을 텍스트와 표로 분류한다.

    Returns:
        (texts, tables) 튜플.
    """
    texts, tables = [], []
    for el in elements:
        el_type = str(type(el))
        if "Table" in el_type:
            tables.append(str(el))
        elif "CompositeElement" in el_type:
            texts.append(str(el))
    return texts, tables


if __name__ == "__main__":
    els = extract_pdf_elements("data/invest.pdf")
    texts, tables = categorize_elements(els)
    print(f"텍스트 청크: {len(texts)}개, 표: {len(tables)}개")
