from apps.backend.algorithm.analyzer import MODE_KEYWORDS, MODE_LEVELS, LevelAnswer, SemanticDetectorError, analyze
from apps.backend.algorithm.keyword_matcher import find_evidence
from apps.backend.algorithm.score_calculator import CriterionInput, CriterionStatus

CRITERIA = [
  CriterionInput("Python", "habilidade", 50, required_level=4),
  CriterionInput("APIs REST", "experiencia", 30, required_level=3),
  CriterionInput("Graduação em TI", "formacao", 20, required_level=3),
]


class FakeDetector:
  source = "fake"

  def __init__(self, level: int, confidence: float = 0.95, levels: dict[str, int] | None = None):
    self.level = level
    self.confidence = confidence
    self.levels = levels or {}
    self.calls: list[str] = []

  def detect(self, resume_text: str, criteria: list[CriterionInput]) -> dict[str, LevelAnswer]:
    self.calls.extend(criterion.name for criterion in criteria)
    return {
      criterion.name: LevelAnswer(level=self.levels.get(criterion.name, self.level), confidence=self.confidence, model_version="fake-1")
      for criterion in criteria
    }


class FailingDetector:
  source = "fake"

  def detect(self, resume_text, criteria):
    raise SemanticDetectorError("fora do ar")


def test_match_ignores_case_and_accents():
  assert find_evidence("Curso de GRADUACAO EM TI na UFSC", "Graduação em TI")
  assert find_evidence("Graduação em TI na UFSC", "graduacao em ti")


def test_match_respects_word_boundaries():
  assert find_evidence("Experiência com JavaScript", "Java") is None
  assert find_evidence("Experiência com C++", "C") is None
  assert find_evidence("Experiência com C++ e C#", "C++")
  assert find_evidence("Trabalhei com Python.", "Python")


def test_match_accepts_flexible_separators():
  assert find_evidence("Desenvolvimento back-end", "back end")
  assert find_evidence("APIs\nREST em produção", "APIs REST")


def test_evidence_comes_from_original_text():
  text = "Atuação em São Paulo com Integração Contínua desde 2020."
  assert "Integração Contínua" in find_evidence(text, "integracao continua")


# Sem detector: só busca por termos, com a presença valendo o peso inteiro.

def test_keyword_mode_sums_weights_of_present_criteria():
  analysis = analyze("Dev Python com APIs REST", CRITERIA)
  assert analysis.mode == MODE_KEYWORDS
  assert analysis.score == 80
  assert [result.status for result in analysis.results] == [CriterionStatus.PRESENT, CriterionStatus.PRESENT, CriterionStatus.ABSENT]
  assert [result.points for result in analysis.results] == [50, 30, 0]
  assert all(result.level is None for result in analysis.results)


def test_keyword_mode_limits():
  assert analyze("Nada relacionado", CRITERIA).score == 0
  assert analyze("Python, APIs REST e Graduação em TI", CRITERIA).score == 100


def test_detector_failure_falls_back_to_keywords():
  analysis = analyze("Dev Python", CRITERIA, FailingDetector())
  assert analysis.mode == MODE_KEYWORDS
  assert analysis.score == 50
  assert analysis.results[0].source == "keyword"


def test_same_input_gives_same_result():
  text = "Dev Python com APIs REST"
  assert analyze(text, CRITERIA) == analyze(text, CRITERIA)


# Com detector: nível estimado, pontos proporcionais até o nível exigido.

def test_detector_evaluates_all_criteria():
  detector = FakeDetector(3)
  analysis = analyze("Dev Python", CRITERIA, detector)
  assert analysis.mode == MODE_LEVELS
  assert detector.calls == ["Python", "APIs REST", "Graduação em TI"]


def test_points_are_proportional_to_required_level():
  # Python exige 4: nível 2 vale metade dos 50 pontos.
  analysis = analyze("Texto", CRITERIA, FakeDetector(3, levels={"Python": 2}))
  python, apis, education = analysis.results
  assert python.status == CriterionStatus.PRESENT
  assert python.points == 25
  assert apis.points == 30
  assert education.points == 20
  assert analysis.score == 75


def test_level_above_required_does_not_add_points():
  junior = analyze("Texto", CRITERIA, FakeDetector(4)).score
  senior = analyze("Texto", CRITERIA, FakeDetector(5)).score
  assert junior == senior == 100


def test_professor_example_junior_and_senior_differ():
  # Mesma presença dos critérios, níveis diferentes: as notas deixam de ser iguais.
  junior = analyze("Texto", CRITERIA, FakeDetector(2)).score
  senior = analyze("Texto", CRITERIA, FakeDetector(5)).score
  assert junior < senior


def test_low_confidence_goes_to_review():
  analysis = analyze("Texto", CRITERIA, FakeDetector(5, confidence=0.79))
  assert all(result.status == CriterionStatus.REVIEW for result in analysis.results)
  assert analysis.score == 0
  assert analyze("Texto", CRITERIA, FakeDetector(5, confidence=0.8)).score == 100


def test_level_zero_without_keyword_is_absent():
  result = analyze("Texto", CRITERIA, FakeDetector(0)).results[0]
  assert result.status == CriterionStatus.ABSENT
  assert result.level == 0


def test_keyword_contradicted_by_detector_goes_to_review():
  criterion = [CriterionInput("Python", "habilidade", 100)]
  result = analyze("Não tenho experiência com Python", criterion, FakeDetector(0)).results[0]
  assert result.status == CriterionStatus.REVIEW
  assert result.source == "fake"
  assert "Python" in result.evidence


def test_missing_answer_goes_to_review():
  class PartialDetector(FakeDetector):
    def detect(self, resume_text, criteria):
      return {"Python": LevelAnswer(level=4, confidence=0.9, model_version="fake-1")}

  analysis = analyze("Texto", CRITERIA, PartialDetector(0))
  assert [result.status for result in analysis.results] == [CriterionStatus.PRESENT, CriterionStatus.REVIEW, CriterionStatus.REVIEW]


def test_suggestions_cover_missing_and_below_level_criteria_by_weight():
  analysis = analyze("Texto", CRITERIA, FakeDetector(3, levels={"Python": 2, "Graduação em TI": 0}))
  assert len(analysis.suggestions) == 2
  assert "Python" in analysis.suggestions[0] and "mais experiência" in analysis.suggestions[0]
  assert "Graduação em TI" in analysis.suggestions[1]
  assert analyze("Texto", CRITERIA, FakeDetector(5)).suggestions == []


def test_details_are_json_ready():
  details = analyze("Dev Python", CRITERIA, FakeDetector(2)).to_details()
  assert details["algorithm_version"] == "3"
  assert details["analysis_mode"] == "levels"
  first = details["criteria"][0]
  assert first["status"] == "present"
  assert first["points"] == 25
  assert first["level"] == 2
  assert first["required_level"] == 4
  assert first["confidence"] == 0.95
  assert "Python" in first["evidence"]
