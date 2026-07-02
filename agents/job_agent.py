from utils.cleaning import clean_skills

def job_analyzer(job_text, ontology_agent):
    skills = ontology_agent.extract_from_text(job_text)
    return clean_skills(skills)