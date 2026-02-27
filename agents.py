from ast import pattern

from click import prompt
from transformers import pipeline

_generator = None

def get_generator():
    global _generator
    if _generator is None:
        _generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-large"
        )
    return _generator

def extract_skills(text):
    import re

    text = re.sub(r"^skills", "", text, flags=re.IGNORECASE).strip()

    words = text.split()
    candidates = []

    for i in range(len(words)):
        # Only 2-word phrases
        if i + 1 < len(words):
            if words[i][0].isupper() and words[i+1][0].isupper():
                phrase = words[i] + " " + words[i+1]
                candidates.append(phrase)

        # Only 3-word phrases
        if i + 2 < len(words):
            if (
                words[i][0].isupper()
                and words[i+1][0].isupper()
                and words[i+2][0].isupper()
            ):
                phrase = words[i] + " " + words[i+1] + " " + words[i+2]
                candidates.append(phrase)
    # Remove duplicates
    candidates = list(dict.fromkeys(candidates))
    # FILTER
    cleaned = []
    for skill in candidates:
        words_in_skill = skill.split()
        # Remove if repeating word
        if len(set(words_in_skill)) != len(words_in_skill):
            continue
        # Remove if too long
        if len(skill) > 40:
            continue
        # Remove obvious garbage combos
        if any(word.lower() in ["skills", "hobbies", "languages"] for word in words_in_skill):
            continue
        cleaned.append(skill)
    print("CLEANED CANDIDATES:", cleaned)

    return cleaned

def clean_skills(skill_list):
    cleaned = set()

    for skill in skill_list:
        skill = skill.strip().lower()
        if not skill[-1].isalpha():
            continue
        cleaned.add(skill)

    final_skills = set(cleaned)
    for skill in cleaned:
        for other in cleaned:
            if skill != other and skill in other:
                if skill in final_skills:
                    final_skills.remove(skill)

    return list(final_skills)

def job_analyzer(job_text, ontology_agent):
    skills = ontology_agent.extract_from_text(job_text)

    if not skills:
        skills = extract_skills(job_text)

    return clean_skills(skills)

def resume_analyzer(skills_text, ontology_agent):
    skills = ontology_agent.extract_from_text(skills_text)

    if not skills:
        skills = extract_skills(skills_text)

    return clean_skills(skills)

import re

def extract_profile(resume_text):
    profile = {
        "role": "",
        "years": "",
        "skills": []
    }

    # Extract years of experience
    match = re.search(r"(\d+)\s+years?", resume_text, re.IGNORECASE)
    if match:
        profile["years"] = match.group(1)

    # Extract role (very naive, just for demo)
    match = re.search(r"I am a ([A-Za-z\s\-]+?)(?: with|\.|,)", resume_text, re.IGNORECASE)
    if match:
        profile["role"] = match.group(1).strip()

    # Extract bullet skills
    skills = re.findall(r"-\s*([A-Za-z0-9 \+\#\.\-]+)", resume_text)
    profile["skills"] = skills[:6]

    return profile


def build_draft(profile, job_text, user_name):
    job_title_match = re.search(r"looking for a ([A-Za-z\s\-]+)", job_text, re.IGNORECASE)
    job_title = job_title_match.group(1) if job_title_match else "this role"

    skills_text = ", ".join(profile["skills"]) if profile["skills"] else "Python and data tools"

    draft = f"""
Dear Hiring Manager,

I am excited to apply for the {job_title}. As a {profile['role']} with {profile['years']} years of experience, I specialize in designing scalable data solutions and Python-based ETL workflows.

My technical expertise includes {skills_text}. I focus on building reliable, maintainable data pipelines that enable faster analytics and informed decision-making.

I am confident that my background aligns well with your requirements and I am eager to contribute to your team’s data engineering initiatives.

Sincerely,
{user_name}
"""
    return draft.strip()

def cover_letter_writer(job_text, resume_text, user_name):
    generator = get_generator()

    # Extract structured profile
    profile = extract_profile(resume_text)
    # Build clean deterministic draft
    draft = build_draft(profile, job_text, user_name)
    # Safety initialization (UnboundLocalError!)
    text = draft  

    try:
        # Step 3: Polish with LLM
        polish_prompt = f"""
You are a professional HR expert.

Rewrite the following draft into a strong, polished, and complete professional cover letter.

Rules:
- Minimum 250 words
- Maximum 350 words
- Keep 4 paragraphs
- Do NOT shorten the content
- Expand details naturally
- Do NOT summarize
- Do NOT use bullet points
- Do NOT repeat phrases
- Do NOT use placeholders
- Keep the applicant name as {user_name}
- Keep it formal and confident

---DRAFT START---
{draft}
---DRAFT END---
"""

        response = generator(
            polish_prompt,
            max_new_tokens=400,
            min_length=250,
            do_sample=False,
            temperature=0.0,
            top_p=0.9,
            repetition_penalty=1.4,
            no_repeat_ngram_size=3,
            early_stopping=True
        )

        generated_text = response[0]["generated_text"].strip()
        cut_markers = ["---", "FINAL VERDICT", "DRAFT START", "DRAFT END"]
        for marker in cut_markers:
            if marker in generated_text:
                generated_text = generated_text.split(marker)[0]

        generated_text = generated_text.strip()
        # Fallback if model output is too short or weird
        if len(generated_text.split()) >= 150:
            text = generated_text

    except Exception as e:
        print("Cover letter generation failed:", e)
        # fallback automatically stays as draft

    # Clean spacing
    text = text.replace("\r", "")
    text = "\n".join([line.strip() for line in text.split("\n")])
    lines = [line for line in text.split("\n") if line.strip() != ""]
    text = "\n\n".join(lines)

    # Remove banned phrases properly
    banned = [
        "I am looking for",
        "looking for a developer",
    ]

    for phrase in banned:
        text = text.replace(phrase, "")

    return text

def skill_matcher(job_enriched, resume_enriched):
    matched = []
    missing = []

    resume_skills_set = {s["skill"] for s in resume_enriched}

    for job in job_enriched:
        job_skill = job["skill"]
        job_related = set(job["related_skills"])

        # Direct match
        if job_skill in resume_skills_set:
            matched.append(job_skill)
            continue

        # Check if any resume skill relates
        found_semantic = False

        for resume in resume_enriched:
            resume_skill = resume["skill"]
            resume_related = set(resume["related_skills"])

            if resume_skill in job_related or job_skill in resume_related:
                matched.append(f"{job_skill} (via {resume_skill})")
                found_semantic = True
                break

        if not found_semantic:
            missing.append(f"{job_skill} (Category: {job['category']})")

    match_percentage = (len(matched) / len(job_enriched)) * 100 if job_enriched else 0

    return {
        "match_percentage": match_percentage,
        "matched_skills": matched,
        "missing_skills": missing
    }

class SkillOntologyAgent:
    def __init__(self, ontology: dict):
        self.ontology = ontology
        self.alias_map = self.build_alias_map()

    def build_alias_map(self):
        alias_map = {}

        for key, value in self.ontology.items():
            alias_map[key] = key  # self mapping

            for alias in value.get("aliases", []):
                alias_map[alias.lower().strip()] = key

        return alias_map

    def normalize(self, skill: str) -> str:
        return skill.lower().strip()

    def canonicalize(self, skill: str) -> str:
        skill = self.normalize(skill)
        # print("Original:", skill) #bruh
        print("Canonical:", self.alias_map.get(skill, skill))
        return self.alias_map.get(skill, skill)
    import re
    def extract_from_text(self, text: str):
        found = set()
        text_lower = text.lower()
        # Normalize punctuation
        text_lower = re.sub(r"[^\w\s]", " ", text_lower)

        for skill_key, data in self.ontology.items():
            skill_phrase = skill_key.replace("_", " ").lower()

             # Exact word match using boundaries
            pattern = rf"\b{re.escape(skill_phrase)}s?\b"
            if re.search(pattern, text_lower):
                found.add(skill_phrase)

            for alias in data.get("aliases", []):
                alias = alias.lower()
                if re.search(rf"\b{re.escape(alias)}\b", text_lower):
                    found.add(skill_phrase)

        return list(found)
    
    def enrich_skills(self, skills: list):
        enriched = []

        for skill in skills:
            canonical = self.canonicalize(skill)

            if canonical in self.ontology:
                enriched.append({
                    "skill": canonical,
                    "category": self.ontology[canonical]["category"],
                    "related_skills": self.ontology[canonical]["related_skills"]
                })
            else:
                enriched.append({
                    "skill": skill,
                    "category": "Unknown",
                    "related_skills": []
                })

        return enriched

