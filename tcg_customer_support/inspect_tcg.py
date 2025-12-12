"""
Inspect paragraphs and styles of the TCG customer support DOCX file.
"""
from pathlib import Path

import docx


def main() -> None:
    root = Path(__file__).resolve().parent.parent.parent
    file_path = root / "TCG 客服场景flow.docx"
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        return

    doc = docx.Document(str(file_path))
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text:
            continue
        style = para.style.name if para.style else ""
        print(f"[{i}] {style} | {text}")


if __name__ == "__main__":
    main()

