import os
import sys
import zipfile
import xml.etree.ElementTree as ET

def extract_docx_text():
    docx_path = r"a:\Complyance\backend\backend_process_alone\PostgreSQL_Transcode_History_Documentation.docx"
    output_path = r"a:\Complyance\extracted_docx.txt"
    if not os.path.exists(docx_path):
        return f"Docx file not found at {docx_path}"
        
    try:
        with zipfile.ZipFile(docx_path) as z:
            doc_xml = z.read("word/document.xml")
            root = ET.fromstring(doc_xml)
            
            # Namespace map
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            # We want to extract paragraphs
            paragraphs_text = []
            
            # Find all paragraph elements
            for p_elem in root.findall('.//w:p', ns):
                p_text = []
                for t_elem in p_elem.findall('.//w:t', ns):
                    if t_elem.text:
                        p_text.append(t_elem.text)
                if p_text:
                    paragraphs_text.append("".join(p_text))
            
            full_content = "\n".join(paragraphs_text)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_content)
            return f"Successfully extracted text to {output_path}"
    except Exception as e:
        return f"Error extracting docx: {str(e)}"

# Run it immediately when imported/run
res = extract_docx_text()
print(res)
with open(r"a:\Complyance\extractor_status.txt", "w") as f:
    f.write(res)
