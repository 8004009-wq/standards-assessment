"""
PDF 解析工具 - 使用 pdfminer.six 提取文本
"""
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import os


def extract_text_from_pdf(file_path: str) -> str:
    """
    从 PDF 文件提取文本
    
    Args:
        file_path: PDF 文件路径
        
    Returns:
        提取的文本内容
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF 文件不存在：{file_path}")
    
    try:
        # 配置 PDF 解析参数
        laparams = LAParams(
            line_overlap=0.5,
            char_margin=2.0,
            line_margin=0.5,
            word_margin=0.1,
            boxes_flow=0.5,
            detect_vertical=True,
            all_texts=True
        )
        
        text = extract_text(file_path, laparams=laparams)
        return text.strip()
    except Exception as e:
        raise Exception(f"PDF 解析失败：{e}")


def extract_text_from_docx(file_path: str) -> str:
    """
    从 Word 文档提取文本
    
    Args:
        file_path: DOCX 文件路径
        
    Returns:
        提取的文本内容
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Word 文件不存在：{file_path}")
    
    try:
        from docx import Document
        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return '\n'.join(paragraphs)
    except Exception as e:
        raise Exception(f"Word 解析失败：{e}")


def extract_text_from_file(file_path: str) -> str:
    """
    根据文件类型自动选择解析器
    
    Args:
        file_path: 文件路径
        
    Returns:
        提取的文本内容
    """
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.lower().endswith('.doc'):
        # .doc 文件需要特殊处理
        raise Exception("不支持 .doc 格式，请转换为 .docx 或 .pdf")
    else:
        raise Exception(f"不支持的文件格式：{file_path}")
