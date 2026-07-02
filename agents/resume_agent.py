from utils.cleaning import clean_skills

def resume_analyzer(sections_dict, full_text, ontology_agent):

    skills_text = sections_dict.get("skills_text", "")

    skills = ontology_agent.extract_from_text(skills_text)

    if not skills:
        skills = ontology_agent.extract_from_text(full_text)

    skills = clean_skills(skills)

    return skills