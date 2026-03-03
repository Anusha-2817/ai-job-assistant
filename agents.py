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

    return clean_skills(skills)

def resume_analyzer(sections_dict, full_text, ontology_agent):
    # Get skills section
    skills_text = sections_dict.get("skills_text", "")
    # Primary ontology extraction
    skills = ontology_agent.extract_from_text(skills_text)
    # Fallback to full resume scan
    if not skills:
        skills = ontology_agent.extract_from_text(full_text)
    # Clean
    skills = clean_skills(skills)

    return skills

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

    import re

    # Extract job title safely
    job_title_match = re.search(r"looking for a ([A-Za-z\s\-]+)", job_text, re.IGNORECASE)
    job_title = job_title_match.group(1).strip() if job_title_match else "Software Engineer"

    role = profile["role"] if profile["role"] else "Software Engineer"
    years = profile["years"] if profile["years"] else "several"

    skills_text = ", ".join(profile["skills"]) if profile["skills"] else "Python and backend development"

    draft = f"""
Dear Hiring Manager,

I am writing to express my interest in the {job_title}. As a {role} with {years} years of experience, I have developed strong skills in building scalable and maintainable software systems.

Throughout my experience, I have worked extensively with technologies such as {skills_text}. I have contributed to backend development, API implementation, database integration, and frontend features while focusing on clean architecture and performance optimization.

I am passionate about writing reliable code, collaborating with cross-functional teams, and continuously improving development processes. I am confident that my technical background and problem-solving skills would allow me to contribute effectively to your engineering team.

Thank you for your time and consideration. I look forward to the opportunity to discuss how I can add value to your organization.

Sincerely,  
{user_name}
"""

    return draft.strip()

def cover_letter_writer(
    job_text,
    resume_text,
    user_name,
    match_data,
    enriched_job_skills,
    enriched_resume_skills
):
    from collections import Counter

    generator = get_generator()

    # --- Extract structured info ---
    profile = extract_profile(resume_text)

    match_percentage = match_data["match_percentage"]
    matched = match_data["matched_skills"]
    missing = match_data["missing_skills"]

    # --- Category grouping from enriched resume ---
    category_map = {}
    for skill in enriched_resume_skills:
        category = skill["category"]
        name = skill["skill"]
        category_map.setdefault(category, []).append(name)

    dominant_categories = Counter(
        [skill["category"] for skill in enriched_resume_skills]
    ).most_common(2)

    # --- Strength Line Based on Match ---
    if match_percentage >= 75:
        strength_line = "My background aligns strongly with the technical requirements of this role."
    elif match_percentage >= 50:
        strength_line = "My experience aligns with several key technical requirements of this role."
    else:
        strength_line = "While I continue to expand my expertise, I bring a solid technical foundation relevant to this role."

    # --- Category Highlight ---
    category_lines = []
    for category, skills in category_map.items():
        category_lines.append(f"{category} ({', '.join(skills[:3])})")

    skills_line = ""
    if category_lines:
        skills_line = "My technical strengths include " + ", ".join(category_lines) + "."

    # --- Growth Line (Missing Skills Awareness) ---
    growth_line = ""
    if missing:
        growth_line = f"I am also actively strengthening my expertise in areas such as {', '.join(missing[:3])}."

    # --- Deterministic Draft ---
    draft = f"""
Dear Hiring Manager,

I am excited to apply for this opportunity. {strength_line}

{skills_line}

{growth_line} I am committed to continuous learning and delivering reliable, maintainable software solutions.

Thank you for your consideration. I look forward to the opportunity to contribute to your team.

Sincerely,
{user_name}
""".strip()

    text = draft  # fallback safety

    # --- Optional LLM Polishing ---
    try:
        polish_prompt = f"""
Rewrite the following draft into a polished professional cover letter.

Rules:
- Do NOT add new experience
- Do NOT invent projects
- Do NOT introduce skills not mentioned
- Keep it 4 paragraphs
- Keep tone formal
- Keep name as {user_name}

DRAFT:
{draft}
"""

        response = generator(
            polish_prompt,
            max_new_tokens=300,
            temperature=0.2,
            do_sample=True
        )

        generated_text = response[0]["generated_text"].strip()

        if len(generated_text.split()) >= 120:
            text = generated_text

    except Exception as e:
        print("Cover letter polishing failed:", e)

    # --- Clean formatting ---
    text = text.replace("\r", "")
    text = "\n".join([line.strip() for line in text.split("\n")])
    lines = [line for line in text.split("\n") if line.strip() != ""]
    text = "\n\n".join(lines)

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

