"""Compara a busca por termos com a busca + Jev, usando apenas os currículos fictícios de resumes.json.

Uso, a partir da raiz do repositório:
  python -m apps.backend.evaluation.compare_jev --repeats 3 --output resultado.json

Faz chamadas reais e pagas à API. O custo é mostrado ao final.
"""

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

from apps.backend.algorithm.analyzer import ABSENT_THRESHOLD, PRESENT_THRESHOLD
from apps.backend.algorithm.anonymizer import redact
from apps.backend.algorithm.keyword_matcher import find_evidence
from apps.backend.algorithm.score_calculator import CriterionInput
from apps.backend.core.config import settings
from apps.backend.integrations.jev import JevDetector

DATASET = Path(__file__).with_name("resumes.json")
USD_PER_MILLION_INPUT_TOKENS = 0.042
LATENCY_LIMIT_SECONDS = 2.0


def classify(probability: float) -> str:
  if probability >= PRESENT_THRESHOLD:
    return "present"
  if probability <= ABSENT_THRESHOLD:
    return "absent"
  return "review"


def collect(language: str, repeats: int) -> dict:
  # Aqui o tempo limite é folgado: a latência é medida, não imposta.
  detector = JevDetector(settings.JEV_SECRET_KEY.get_secret_value(), settings.JEV_MODEL, 30.0, language=language)
  decisions, latencies, tokens, version = [], [], 0, None

  for vacancy in json.loads(DATASET.read_text(encoding="utf-8"))["vacancies"]:
    criteria = [CriterionInput(**item) for item in vacancy["criteria"]]
    for resume in vacancy["resumes"]:
      sent = redact(resume["text"], (resume["person"],))
      runs = []
      for _ in range(repeats):
        started = time.perf_counter()
        result = detector.ask(sent, criteria)
        latencies.append(time.perf_counter() - started)
        tokens += result.input_tokens
        runs.append(result)
      version = runs[0].answers[criteria[0].name].model_version
      for criterion, label in zip(criteria, resume["labels"]):
        probabilities = [run.answers[criterion.name].probability for run in runs]
        decisions.append({
          "resume": resume["id"],
          "criterion": criterion.name,
          "weight": criterion.weight,
          "label": label,
          "keyword": find_evidence(resume["text"], criterion.name) is not None,
          "probabilities": probabilities,
          "statuses": [classify(probability) for probability in probabilities],
        })
  return {"language": language, "model": version, "decisions": decisions, "latencies": latencies, "input_tokens": tokens}


def predict(decision: dict, strategy: str) -> str:
  """Devolve present, absent ou review para a primeira repetição de cada estratégia."""
  jev = decision["statuses"][0]
  if strategy == "keyword":
    return "present" if decision["keyword"] else "absent"
  if strategy == "jev":
    return jev
  if strategy == "jev_when_no_keyword":
    return "present" if decision["keyword"] else jev
  # "keyword+jev": a regra de conflito usada em analyzer.py.
  if decision["keyword"]:
    return "review" if jev == "absent" else "present"
  return jev


def metrics(decisions: list[dict], strategy: str) -> dict:
  labeled = [item for item in decisions if item["label"] is not None]
  tp = fp = fn = tn = review = 0
  for item in labeled:
    prediction = predict(item, strategy)
    review += prediction == "review"
    # "A revisar" não pontua, como no sistema.
    present = prediction == "present"
    tp += present and item["label"]
    fp += present and not item["label"]
    fn += not present and item["label"]
    tn += not present and not item["label"]

  by_resume: dict[str, float] = {}
  for item in labeled:
    points = item["weight"] if predict(item, strategy) == "present" else 0
    expected = item["weight"] if item["label"] else 0
    by_resume[item["resume"]] = by_resume.get(item["resume"], 0) + points - expected

  return {
    "accuracy": (tp + tn) / len(labeled),
    "precision": tp / (tp + fp) if tp + fp else None,
    "recall": tp / (tp + fn) if tp + fn else None,
    "false_positives": fp,
    "false_negatives": fn,
    "review": review,
    "decisions": len(labeled),
    "score_mean_abs_error": statistics.mean(abs(value) for value in by_resume.values()),
    "score_max_abs_error": max(abs(value) for value in by_resume.values()),
  }


def consistency(decisions: list[dict]) -> dict:
  spreads = [max(item["probabilities"]) - min(item["probabilities"]) for item in decisions]
  return {
    "max_probability_spread": max(spreads),
    "identical_probabilities": sum(spread == 0 for spread in spreads),
    "status_changed": sum(len(set(item["statuses"])) > 1 for item in decisions),
    "decisions": len(decisions),
  }


def percentile(values: list[float], fraction: float) -> float:
  ordered = sorted(values)
  return ordered[min(len(ordered) - 1, int(len(ordered) * fraction))]


def report(run: dict) -> dict:
  latencies = run["latencies"]
  return {
    "language": run["language"],
    "model": run["model"],
    "strategies": {name: metrics(run["decisions"], name) for name in ("keyword", "jev", "jev_when_no_keyword", "keyword+jev")},
    "consistency": consistency(run["decisions"]),
    "latency_seconds": {
      "p50": statistics.median(latencies),
      "p95": percentile(latencies, 0.95),
      "max": max(latencies),
      "over_limit": sum(value > LATENCY_LIMIT_SECONDS for value in latencies),
      "requests": len(latencies),
    },
    "input_tokens": run["input_tokens"],
    "estimated_cost_usd": run["input_tokens"] * USD_PER_MILLION_INPUT_TOKENS / 1_000_000,
  }


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--repeats", type=int, default=3)
  parser.add_argument("--languages", nargs="+", default=["en", "pt"])
  parser.add_argument("--output", type=Path)
  args = parser.parse_args()

  if settings.JEV_SECRET_KEY is None:
    sys.exit("Defina JEV_SECRET_KEY em apps/backend/.env")

  runs = [collect(language, args.repeats) for language in args.languages]
  summary = [report(run) for run in runs]
  print(json.dumps(summary, indent=2, ensure_ascii=False))
  if args.output:
    args.output.write_text(json.dumps({"summary": summary, "runs": runs}, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
  main()
