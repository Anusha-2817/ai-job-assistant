# import re
# import json
# import fitz  # PyMuPDF


# class ResumeIngestionAgent:

#     # 1. Parse PDF
#     def parse_pdf(self, file_path: str) -> str:
#         try:
#             doc = fitz.open(file_path)
#         except Exception as e:
#             raise ValueError(f"Invalid or corrupted PDF file: {file_path}") from e

#         text = ""
#         for page in doc:
#             text += page.get_text()

#         return text

#     # 2. Clean Text
#     def clean_text(self, text: str) -> str:
#         text = re.sub(r'\s+', ' ', text)
#         text = text.replace("•", "")
#         return text.strip()

#     # 3. Split Sections (Basic)

#     def split_sections(self, text: str) -> dict:
#         sections = {
#             "skills_text": "",
#             "experience_text": "",
#             "education_text": "",
#             "projects_text": ""
#         }

#         lower_text = text.lower()

#         # Find keyword positions
#         def find_first(text, terms):
#             positions = [text.find(term) for term in terms if text.find(term) != -1]
#             return min(positions) if positions else -1

#         keywords = {
#             "skills_text": find_first(lower_text, ["skills"]),
#             "experience_text": find_first(lower_text, ["employment history", "experience"]),
#             "education_text": find_first(lower_text, ["education"]),
#             "projects_text": find_first(lower_text, ["projects"])
#         }
#         # Remove not found sections
#         keywords = {k: v for k, v in keywords.items() if v != -1}
#         # Sort by position in text
#         sorted_sections = sorted(keywords.items(), key=lambda x: x[1])

#         for i, (section_name, start_pos) in enumerate(sorted_sections):
#             end_pos = sorted_sections[i + 1][1] if i + 1 < len(sorted_sections) else len(text)
#             content = text[start_pos:end_pos].strip()
#             sections[section_name] = content

#         return sections

#     def process_resume(self, file_path: str) -> dict:
#         raw_text = self.parse_pdf(file_path)
#         cleaned_text = self.clean_text(raw_text)
#         sections = self.split_sections(cleaned_text)
#         # Trim skills_text further
#         skills_text = sections["skills_text"].lower()
#         stop_terms = ["hobbies", "languages", "achievements","qualifications"]
#         for term in stop_terms:
#             idx = skills_text.find(term)
#             if idx != -1:
#                 sections["skills_text"] = sections["skills_text"][:idx]
#                 break
#         return sections