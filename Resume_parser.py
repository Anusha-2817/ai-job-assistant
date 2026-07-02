import re
from docx import Document


class ResumeIngestionAgent:

    # 1️⃣ Parse DOCX (Paragraphs + Tables)
    def parse_docx(self, file_path: str) -> str:
        doc = Document(file_path)
        full_text = []
        for i, para in enumerate(doc.paragraphs):
            full_text.append(para.text)
        return "\n".join(full_text)

    # 2️⃣ Clean Text (Preserve structure!)
    def clean_text(self, text: str) -> str:
        text = text.replace("\t", " ")
        text = re.sub(r'[ ]+', ' ', text)   # collapse multiple spaces
        text = re.sub(r'\n\s*\n', '\n', text)  # remove empty lines safely
        return text.strip()

    # 3️⃣ Split Sections Using Regex Headings
    def split_sections(self, text: str) -> dict:
        sections = {
            "skills_text": "",
            "experience_text": "",
            "education_text": "",
            "projects_text": ""
        }

        # Define heading patterns
        heading_patterns = {
            "skills_text": r'^\s*(skills)\s*$',
            "experience_text": r'^\s*(experience|work experience|employment history)\s*$',
            "education_text": r'^\s*(education|academic background)\s*$',
            "projects_text": r'^\s*(projects)\s*$'
        }

        lines = text.split("\n")
        current_section = None

        for line in lines:
            clean_line = line.strip()

            # Check if line matches any heading
            for section, pattern in heading_patterns.items():
                if re.match(pattern, clean_line, re.IGNORECASE):
                    current_section = section
                    break

            # Append content to current section
            if current_section and clean_line:
                sections[current_section] += clean_line + "\n"

        return sections

    # 4️⃣ Fallback: Scan entire resume for ontology hits
    def fallback_full_scan(self, text: str, ontology_list: list) -> list:
        found = []
        lower_text = text.lower()

        for skill in ontology_list:
            if skill.lower() in lower_text:
                found.append(skill)

        return list(set(found))

    # 5️⃣ Main Process
    def process_resume(self, file_path: str) -> dict:
        # import os

        # print("ABS PATH:", os.path.abspath(file_path))
        # print("FILE SIZE:", os.path.getsize(file_path))
        raw_text = self.parse_docx(file_path)
        cleaned_text = self.clean_text(raw_text)
        sections = self.split_sections(cleaned_text)

        print("\n=== RAW TEXT PREVIEW ===")
        print(cleaned_text[:500])

       

        return {
            "sections": sections,
            "full_text": cleaned_text
        }