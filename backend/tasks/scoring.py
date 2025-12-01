# backend/tasks/scoring.py
from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Any
import math

DEFAULT_IMPORTANCE = 5
DEFAULT_ESTIMATED_HOURS = 4
FAR_FUTURE_DAYS = 365 * 5

STRATEGIES = {
    "smart_balance": {"w_u": 0.35, "w_i": 0.30, "w_e": 0.20, "w_d": 0.15},
    "fastest_wins":  {"w_u": 0.20, "w_i": 0.15, "w_e": 0.50, "w_d": 0.15},
    "high_impact":   {"w_u": 0.15, "w_i": 0.65, "w_e": 0.10, "w_d": 0.10},
    "deadline_driven":{"w_u":0.70, "w_i":0.15, "w_e":0.05, "w_d":0.10},
}

def safe_parse_date(d):
    if not d:
        return None
    if isinstance(d, date):
        return d
    try:
        # accept "YYYY-MM-DD" or ISO
        return datetime.fromisoformat(d).date()
    except Exception:
        # try common formats (robustness)
        from dateutil import parser
        try:
            return parser.parse(d).date()
        except Exception:
            return None

def normalize_importance(importance):
    try:
        imp = float(importance)
    except Exception:
        imp = DEFAULT_IMPORTANCE
    imp = max(1.0, min(10.0, imp))
    return (imp - 1.0) / 9.0

def urgency_score(due_date: date, today: date) -> float:
    if due_date is None:
        days = FAR_FUTURE_DAYS
    else:
        days = (due_date - today).days
    if days <= -30:
        return 1.0
    if days >= 365:
        return 0.0
    days_norm = (days + 30) / (365 + 30)
    urgency = 1.0 - days_norm
    return max(0.0, min(1.0, urgency))

def effort_score(hours) -> float:
    try:
        h = float(hours)
    except Exception:
        h = DEFAULT_ESTIMATED_HOURS
    if h <= 0:
        return 1.0
    if h >= 40:
        return 0.0
    return max(0.0, min(1.0, 1.0 - (h - 0.25) / (40 - 0.25)))

def detect_cycles(tasks: List[Dict]) -> Tuple[set, List[List[Any]]]:
    graph = {}
    for t in tasks:
        tid = t.get("id") or t.get("title")
        graph[tid] = list(t.get("dependencies") or [])

    visited = set()
    onstack = set()
    cycles = []
    cycle_nodes = set()

    def dfs(u, stack):
        if u in onstack:
            if u in stack:
                idx = stack.index(u)
                cyc = stack[idx:] + [u]
            else:
                cyc = stack + [u]
            cycles.append(cyc)
            for n in cyc:
                cycle_nodes.add(n)
            return
        if u in visited:
            return
        visited.add(u)
        onstack.add(u)
        stack.append(u)
        for v in graph.get(u, []):
            if v not in graph:
                continue
            dfs(v, stack)
        stack.pop()
        onstack.remove(u)

    for node in list(graph.keys()):
        if node not in visited:
            dfs(node, [])
    return cycle_nodes, cycles

def compute_dependency_scores(tasks: List[Dict]) -> Dict[Any, float]:
    prereq_to_dependents = {}
    ids = [t.get("id") or t.get("title") for t in tasks]
    for t in tasks:
        tid = t.get("id") or t.get("title")
        deps = t.get("dependencies") or []
        for d in deps:
            prereq_to_dependents.setdefault(d, []).append(tid)
    dep_score = {}
    for node in ids:
        visited = set()
        queue = list(prereq_to_dependents.get(node, []))
        while queue:
            cur = queue.pop(0)
            if cur in visited:
                continue
            visited.add(cur)
            queue.extend(prereq_to_dependents.get(cur, []))
        dep_score[node] = len(visited) / max(1, len(tasks)-1)
    return dep_score

def analyze_tasks(tasks: List[Dict], strategy: str = "smart_balance", today: date = None) -> List[Dict]:
    today = today or datetime.utcnow().date()
    weights = STRATEGIES.get(strategy, STRATEGIES["smart_balance"])
    normalized = []
    for t in tasks:
        tid = t.get("id") or t.get("title")
        nd = {
            "raw": t,
            "id": tid,
            "title": t.get("title", f"untitled-{tid}"),
            "due_date": safe_parse_date(t.get("due_date")),
            "importance": normalize_importance(t.get("importance")),
            "estimated_hours": t.get("estimated_hours") or DEFAULT_ESTIMATED_HOURS,
            "dependencies": t.get("dependencies") or [],
        }
        normalized.append(nd)

    cycle_nodes, cycles = detect_cycles(tasks)
    dep_scores = compute_dependency_scores(tasks)

    results = []
    for nd in normalized:
        tid = nd["id"]
        u = urgency_score(nd["due_date"], today)
        i = nd["importance"]
        e = effort_score(nd["estimated_hours"])
        d = dep_scores.get(tid, 0.0)
        score = (weights["w_u"] * u + weights["w_i"] * i + weights["w_e"] * e + weights["w_d"] * d)
        explanation_parts = []
        if nd["due_date"] is None:
            explanation_parts.append("No due date provided (treated as low-urgency).")
        else:
            days = (nd["due_date"] - today).days
            if days < 0:
                explanation_parts.append(f"Past due by {-days} day(s) — urgent.")
            else:
                explanation_parts.append(f"Due in {days} day(s).")
        explanation_parts.append(f"Importance normalized={i:.2f}.")
        explanation_parts.append(f"Effort-score={e:.2f} (lower hours => higher quick-win).")
        if d > 0:
            explanation_parts.append(f"Blocks/unlocks other tasks (dependency score={d:.2f}).")
        circular = tid in cycle_nodes
        if circular:
            score *= 0.55
            explanation_parts.append("Part of a circular dependency — penalized until resolved.")
        result = {
            "id": tid,
            "title": nd["title"],
            "raw": nd["raw"],
            "score": round(score, 4),
            "components": {"urgency": round(u,4), "importance": round(i,4), "effort": round(e,4), "dependency": round(d,4)},
            "explanation": " ".join(explanation_parts),
            "circular": circular,
        }
        results.append(result)
    results.sort(key=lambda r: (r["score"], not r["circular"]), reverse=True)
    return results
