import json
from pathlib import Path
from statistics import mean

from app.search import rank


def main():
    cases = json.loads(Path(__file__).with_name("cases.json").read_text(encoding="utf-8"))
    jobs = {
        "backend": {"id": "backend", "skills": ["python", "fastapi", "postgresql"]},
        "frontend": {"id": "frontend", "skills": ["react", "typescript"]},
        "ai": {"id": "ai", "skills": ["python", "typescript"]},
    }
    baselines = []
    personalized = []
    missed = []
    for case in cases:
        relevant = set(case["relevant"])
        baseline = case["semantic"][:3]
        ranked = rank([jobs[key] for key in case["semantic"]],
                      [jobs[key] for key in case["lexical"]], case["skills"], limit=3)
        final = [job["id"] for job in ranked]
        for ids, scores in ((baseline, baselines), (final, personalized)):
            scores.append(next((1 / position for position, key in enumerate(ids, 1)
                                if key in relevant), 0))
        if not final or final[0] != case["expected_first"]:
            missed.append(case["name"])
    print(f"Semantic-only MRR@3: {mean(baselines):.3f}")
    print(f"Personalized hybrid MRR@3: {mean(personalized):.3f}")
    if missed:
        raise SystemExit("Unexpected top result: " + ", ".join(missed))


if __name__ == "__main__":
    main()
