from collections import defaultdict


def rank(semantic, lexical, skills, limit=8):
    scores = defaultdict(float)
    jobs = {}
    for stream in (semantic, lexical):
        for position, job in enumerate(stream, 1):
            jobs[job["id"]] = job
            scores[job["id"]] += 1 / (30 + position)
    for job_id, job in jobs.items():
        overlap = sorted(set(job["skills"]) & set(skills))
        job["matched_skills"] = overlap
        scores[job_id] += 0.02 * len(overlap) / max(1, len(set(skills)))
    ordered = sorted(jobs, key=lambda key: (-scores[key], key))
    return [dict(jobs[key], score=round(scores[key], 5)) for key in ordered[:limit]]


def validate_answer(answer, results):
    if not isinstance(answer, dict) or not isinstance(answer.get("summary"), str):
        raise ValueError("Invalid response")
    picks = answer.get("picks")
    if not isinstance(picks, list) or len(picks) > 5:
        raise ValueError("Invalid recommendations")
    by_id = {job["id"]: job for job in results}
    seen = set()
    grounded = []
    for pick in picks:
        if not isinstance(pick, dict):
            raise ValueError("Invalid recommendation")
        key = pick.get("id")
        reason = pick.get("reason")
        if not isinstance(key, str) or key not in by_id or key in seen or not isinstance(reason, str) or not reason.strip():
            raise ValueError("Recommendation must cite a unique retrieved job")
        seen.add(key)
        grounded.append(dict(by_id[key], reason=reason))
    return {"summary": answer["summary"], "jobs": grounded}
