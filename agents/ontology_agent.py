import re
from utils.cleaning import (
    clean_text,
    generate_candidates,
    normalize_phrase
)


class SkillOntologyAgent:

    def __init__(self, ontology: dict):

        self.ontology = ontology

        self.alias_map = self.build_alias_map()

    def build_alias_map(self):

        alias_map = {}

        for canonical_skill, value in self.ontology.items():

            # Self mapping
            alias_map[canonical_skill.lower()] = canonical_skill

            for alias in value.get("aliases", {}):

                alias_map[
                    alias.lower().strip()
                ] = canonical_skill

        return alias_map

    def resolve_candidate(self, candidate: str):
        

        candidate = normalize_phrase(candidate)

        # ---------------------------------
        # 1. EXACT ALIAS MATCH
        # ---------------------------------
        if candidate in self.alias_map:
            return self.alias_map[candidate]

        candidate_tokens = set(candidate.split())

        best_match = None
        best_score = 0

        # ---------------------------------
        # 2. PARTIAL / TOKEN MATCH
        # ---------------------------------
        for ontology_skill, value in self.ontology.items():

            possible_phrases = [ontology_skill]

            aliases = value.get("aliases", {}).keys()

            possible_phrases.extend(aliases)

            for phrase in possible_phrases:

                normalized_phrase = normalize_phrase(
                    phrase.lower()
                )

                ontology_tokens = set(
                    normalized_phrase.split()
                )

                overlap = len(
                    candidate_tokens & ontology_tokens
                )

                score = overlap / max(
                    len(candidate_tokens),
                    len(ontology_tokens)
                )

                if score > best_score:

                    best_score = score

                    # Store canonical skill
                    best_match = ontology_skill

        # ---------------------------------
        # 3. MATCH THRESHOLD
        # ---------------------------------
        if best_score >= 0.5:
            return best_match

        return None

    def extract_from_text(self, text: str):

        found = set()

        # STEP 1 — CLEAN
        cleaned_text = clean_text(text)

        # STEP 2 — GENERATE CANDIDATES
        candidates = generate_candidates(cleaned_text)

        # STEP 3 — RESOLVE
        for candidate in candidates:

            resolved_skill = self.resolve_candidate(candidate)

            if resolved_skill:
                found.add(resolved_skill)
        print(candidates)
        return list(found)

    def enrich_skills(self, skills: list):

        enriched = []

        for skill in skills:

            if skill in self.ontology:

                enriched.append({
                    "skill": skill,
                    "category": self.ontology[skill]["category"],
                    "related_skills": self.ontology[skill]["related_skills"]
                })

            else:

                enriched.append({
                    "skill": skill,
                    "category": "Unknown",
                    "related_skills": []
                })

        return enriched