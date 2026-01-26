from agents import (
    job_analyzer,
    resume_analyzer,
    cover_letter_writer,
    skill_matcher
)


def skill_matcher(job_skills, resume_skills):
    job_set = set(s.strip().lower() for s in job_skills.split(","))
    resume_set = set(s.strip().lower() for s in resume_skills.split(","))

    matched = job_set & resume_set

    return {
        "matched_skills": list(matched),
        "match_percent": round(len(matched) / max(len(job_set), 1) * 100, 2)
    }

def coordinator(job_text, resume_text):

    print("\n--- Running Job Analyzer Agent ---")
    job_result = job_analyzer(job_text)
    print("Job Skills:", job_result)

    print("\n--- Running Resume Analyzer Agent ---")
    resume_result = resume_analyzer(resume_text)
    print("Resume Skills:", resume_result)
    

    print("\n--- Running Cover Letter Agent ---")
    cover_letter = cover_letter_writer(job_text, resume_text)
    print("\nGenerated Cover Letter:\n", cover_letter)
    print("\n--- Running Skill Matcher Agent ---")

    print("\n--- Running Skill Matcher Agent ---")
    match_result = skill_matcher(job_result, resume_result)
    print("Skill Match:", match_result)

    return {
    "job_skills": job_result,
    "resume_skills": resume_result,
    "skill_match": match_result,
    "cover_letter": cover_letter
}


if __name__ == "__main__":

    sample_job = """
    We are hiring a Python Developer with skills in
    Machine Learning, Flask, APIs, and Data Analysis.
    """

    sample_resume = """
    I am a student who knows Python, Pandas, and basic ML.
    I have built small projects in data visualization.
    """

    coordinator(sample_job, sample_resume)
