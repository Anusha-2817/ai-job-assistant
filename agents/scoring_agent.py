def skill_matcher(job_enriched, resume_enriched):

    matched = []
    missing = []

    total_score = 0
    max_score = len(job_enriched)

    resume_skills_set = {s["skill"] for s in resume_enriched}

    for job in job_enriched:

        job_skill = job["skill"]
        job_related = job["related_skills"]
        print(job_skill, type(job_related), job_related)

        best_score = 0
        best_match = None
        match_type = None

        # EXACT MATCH
        if job_skill in resume_skills_set:

            best_score = 1.0
            best_match = job_skill
            match_type = "exact"

        else:

            # WEIGHTED RELATED MATCH
            for resume in resume_enriched:

                resume_skill = resume["skill"]

                if resume_skill in job_related:

                    relation_weight = job_related[resume_skill]

                    if (
                        relation_weight > best_score
                        and relation_weight >= 0.7
                    ):

                        best_score = relation_weight
                        best_match = resume_skill
                        match_type = "related"

        # STORE RESULTS
        if best_score > 0:

            total_score += best_score

            matched.append({
                "job_skill": job_skill,
                "matched_with": best_match,
                "match_type": match_type,
                "score": round(best_score, 2)
            })

        else:

            missing.append({
                "job_skill": job_skill,
                "category": job["category"]
            })

    match_percentage = (
        (total_score / max_score) * 100
        if max_score > 0 else 0
    )

    return {
        "match_percentage": round(match_percentage, 2),
        "matched_skills": matched,
        "missing_skills": missing
    }