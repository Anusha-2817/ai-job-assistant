
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
