import re

# Common filler / weak words
STOPWORDS = {
    "and", "or", "with", "using", "in", "on", "at",
    "to", "for", "of", "the", "a", "an",
    "experience", "ability", "knowledge",
    "working", "building", "developing",
    "candidate", "looking", "strong"
}

# Words that usually indicate non-skill phrases
WEAK_STARTERS = {
    "experience", "ability", "knowledge",
    "understanding", "candidate", "working"
}

VERB_HEAVY_WORDS = {
    "developing",
    "working",
    "managing",
    "creating",
    "designing",
    "leading",
    "building",
    "implementing",
    "contributing",
    "collaborating"
    "experienced"
    "skilled"
    "proficient"
}

def clean_text(text: str) -> str:
    """
    Basic JD normalization
    """

    text = text.lower()

    # Remove punctuation
    text = re.sub(r"[^\w\s]", " ", text)

    # Collapse spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def generate_candidates(text: str):
    """
    Generate meaningful n-gram candidates
    """

    words = text.split()

    candidates = set()

    # Generate 2,3,4 grams
    for n in range(2, 5):

        for i in range(len(words) - n + 1):

            phrase_words = words[i:i+n]

            # Skip weak starters
            if phrase_words[0] in WEAK_STARTERS:
                continue

            # Skip all-stopword phrases
            if all(word in STOPWORDS for word in phrase_words):
                continue

            # Skip phrases with too many weak words
            weak_count = sum(
                1 for word in phrase_words
                if word in STOPWORDS
            )

            if weak_count >= 2:
                continue

            # Skip verb-heavy phrases
            verb_count = sum(
                1 for word in phrase_words
                if word in VERB_HEAVY_WORDS
            )

            if verb_count >= 2:
                continue

            phrase = " ".join(phrase_words)

            candidates.add(phrase)

    return list(candidates)


def normalize_phrase(phrase: str):
    """
    Canonical phrase normalization
    """

    phrase = phrase.lower().strip()

    # Remove extra spaces
    phrase = re.sub(r"\s+", " ", phrase)

    # Remove filler adjectives
    REMOVE_WORDS = {
        "scalable",
        "distributed",
        "modern",
        "robust",
        "efficient",
        "advanced",
        "strong",
        "complex"
    }

    words = [
        word for word in phrase.split()
        if word not in REMOVE_WORDS
    ]

    # Simple plural normalization
    normalized = []

    for word in words:

        if word.endswith("systems"):
            word = "system"

        elif word.endswith("apis"):
            word = "api"

        elif word.endswith("services"):
            word = "service"

        elif word.endswith("pipelines"):
            word = "pipeline"

        normalized.append(word)

    phrase = " ".join(normalized)

    return phrase


def clean_skills(skill_list):
    """
    Final cleanup after ontology matching
    """

    cleaned = set()

    for skill in skill_list:

        skill = skill.strip().lower()

        if len(skill) < 2:
            continue

        if not skill[-1].isalnum():
            continue

        cleaned.add(skill)

    # Remove smaller duplicates
    final_skills = set(cleaned)

    for skill in cleaned:

        for other in cleaned:

            if skill != other and skill in other:

                if skill in final_skills:
                    final_skills.remove(skill)

    return list(final_skills)