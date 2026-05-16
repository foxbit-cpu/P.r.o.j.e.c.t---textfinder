import os
import re
import docx2txt
import PyPDF2

def search_files(folder, query, whole_word=False, extensions=(".txt", ".py", ".md", ".log", ".csv", ".ini", ".json", ".xml", ".cfg", ".rst", ".tex", ".docx", ".pdf")):
    results = []
    if whole_word:
        pattern = r'\b' + re.escape(query) + r'\b'
        search_func = lambda text: re.search(pattern, text, re.IGNORECASE) is not None
    else:
        query_lower = query.lower()
        search_func = lambda text: query_lower in text.lower()

    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(extensions):
                filepath = os.path.join(root, file)
                file_text = ""
                try:
                    if file.lower().endswith('.docx'):
                        file_text = docx2txt.process(filepath)   # без склейки – абзацы сохраняются
                    elif file.lower().endswith('.pdf'):
                        with open(filepath, 'rb') as f:
                            reader = PyPDF2.PdfReader(f)
                            text_parts = []
                            for page in reader.pages:
                                text_parts.append(page.extract_text() or "")
                        file_text = "\n".join(text_parts)       # сохраняем переводы строк
                    else:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            file_text = f.read()
                    if search_func(file_text):
                        results.append((filepath, os.path.getsize(filepath)))
                except Exception:
                    continue
    return results