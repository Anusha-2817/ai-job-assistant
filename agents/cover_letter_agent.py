from collections import Counter
from models.generator import get_generator
from utils.profile_extractor import extract_profile


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
        growth_line = f"I am also actively strengthening my expertise in areas such as {', '.join(
    skill["job_skill"]
    for skill in missing[:3]
)}."

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