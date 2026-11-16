"""Mede se o Jev estima o nível certo de cada critério, usando apenas os currículos fictícios de levels.json.

Uso, a partir da raiz do repositório:
  python -m apps.backend.evaluation.compare_levels --repeats 3 --output resultado.json

Faz chamadas reais e pagas à API. O custo é mostrado ao final.
Os currículos e rótulos foram escritos pela equipe do projeto: o resultado não é uma medição independente.
"""

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

from apps.backend.algorithm.analyzer import MIN_CONFIDENCE
from apps.backend.algorithm.anonymizer import redact
from apps.backend.algorithm.score_calculator import CriterionInput, CriterionResult, CriterionStatus, calculate_score
from apps.backend.core.config import settings
from apps.backend.integrations.jev import JevDetector

DATASET = Path(__file__).with_name("levels.json")
USD_PER_MILLION_INPUT_TOKENS = 0.042


def collect(data: dict, repeats: int) -> dict:
  # Aqui o tempo limite é folgado: a latência é medida, não imposta.
  detector = JevDetector(settings.JEV_SECRET_KEY.get_secret_value(), settings.JEV_MODEL, 30.0)
  # O peso não muda a pergunta ao Jev; as notas por vaga usam os pesos de cada vaga.
  criteria = [CriterionInput(item["name"], item["criterion_type"], weight=1) for item in data["criteria"]]
  rows, latencies, tokens, version = [], [], 0, None

  for resume in data["resumes"]:
    sent = redact(resume["text"], (resume["person"],))
    runs = []
    for _ in range(repeats):
      started = time.perf_counter()
      result = detector.ask(sent, criteria)
      latencies.append(time.perf_counter() - started)
      tokens += result.input_tokens
      runs.append(result.answers)
    version = runs[0][criteria[0].name].model_version
    for criterion in criteria:
      rows.append({
        "resume": resume["id"],
        "group": resume["group"],
        "criterion": criterion.name,
        "label": resume["levels"][criterion.name],
        "levels": [run[criterion.name].level for run in runs],
        "confidence": [round(run[criterion.name].confidence, 2) for run in runs],
      })
  return {"model": version, "rows": rows, "latencies": latencies, "input_tokens": tokens}


def accuracy(rows: list[dict]) -> dict:
  labeled = [row for row in rows if row["label"] is not None]
  confident = [row for row in labeled if row["confidence"][0] >= MIN_CONFIDENCE]
  return {
    "decisions": len(labeled),
    "exact": sum(row["levels"][0] == row["label"] for row in labeled) / len(labeled),
    "within_one": sum(abs(row["levels"][0] - row["label"]) <= 1 for row in labeled) / len(labeled),
    "confident": len(confident),
    "confident_exact": sum(row["levels"][0] == row["label"] for row in confident) / len(confident) if confident else None,
    "level_changed_between_repeats": sum(len(set(row["levels"])) > 1 for row in rows),
  }


def vacancy_scores(data: dict, rows: list[dict]) -> dict:
  """Nota de cada currículo em cada vaga: pelos rótulos e pelo Jev (1ª repetição), com a mesma fórmula do sistema."""
  by_resume: dict[str, dict] = {}
  for row in rows:
    by_resume.setdefault(row["resume"], {})[row["criterion"]] = row

  def score(spec: list[dict], levels: dict[str, int | None], confidences: dict[str, float]) -> float:
    results = []
    for item in spec:
      level, confidence = levels[item["name"]], confidences[item["name"]]
      status = CriterionStatus.PRESENT if level and confidence >= MIN_CONFIDENCE else CriterionStatus.ABSENT
      results.append(CriterionResult(item["name"], "", item["weight"], status, "jev", item["required_level"], level=level))
    return calculate_score(results)

  scores = {}
  for resume_id, items in by_resume.items():
    expected = {name: row["label"] if row["label"] is not None else row["levels"][0] for name, row in items.items()}
    predicted = {name: row["levels"][0] for name, row in items.items()}
    confidences = {name: row["confidence"][0] for name, row in items.items()}
    always = {name: 1.0 for name in items}
    scores[resume_id] = {
      vacancy: {"expected": score(spec, expected, always), "jev": score(spec, predicted, confidences)}
      for vacancy, spec in data["vacancies"].items()
    }
  return scores


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--repeats", type=int, default=3)
  parser.add_argument("--output", type=Path)
  args = parser.parse_args()

  if settings.JEV_SECRET_KEY is None:
    sys.exit("Defina JEV_SECRET_KEY em apps/backend/.env")

  data = json.loads(DATASET.read_text(encoding="utf-8"))
  run = collect(data, args.repeats)
  rows = run["rows"]
  summary = {
    "model": run["model"],
    "accuracy": {group: accuracy([row for row in rows if row["group"] == group]) for group in ("simples", "dificil")},
    "errors": [row for row in rows if row["label"] is not None and any(level != row["label"] for level in row["levels"])],
    "vacancy_scores": vacancy_scores(data, rows),
    "latency_seconds": {"p50": statistics.median(run["latencies"]), "max": max(run["latencies"]), "requests": len(run["latencies"])},
    "input_tokens": run["input_tokens"],
    "estimated_cost_usd": run["input_tokens"] * USD_PER_MILLION_INPUT_TOKENS / 1_000_000,
  }
  print(json.dumps(summary, indent=2, ensure_ascii=False))
  if args.output:
    args.output.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
  main()
