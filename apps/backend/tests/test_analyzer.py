from apps.backend.algorithm.analyzer import SemanticAnswer, analyze
from apps.backend.algorithm.keyword_matcher import find_evidence
from apps.backend.algorithm.score_calculator import CriterionInput, CriterionStatus

CRITERIA = [
  CriterionInput("Python", "habilidade", 50),
  CriterionInput("APIs REST", "experiencia", 30),
  CriterionInput("Graduação em TI", "formacao", 20),
]


class FakeDetector:
  source = "fake"

  def __init__(self, probability: float):
    self.probability = probability
    self.calls: list[str] = []

  def detect(self, resume_text: str, criterion: CriterionInput) -> SemanticAnswer:
    self.calls.append(criterion.name)
    return SemanticAnswer(probability=self.probability, model_version="fake-1")


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


def test_score_sums_weights_of_present_criteria():
  analysis = analyze("Dev Python com APIs REST", CRITERIA)
  assert analysis.score == 80
  assert [result.status for result in analysis.results] == [CriterionStatus.PRESENT, CriterionStatus.PRESENT, CriterionStatus.ABSENT]
  assert [result.points for result in analysis.results] == [50, 30, 0]


def test_score_limits():
  assert analyze("Nada relacionado", CRITERIA).score == 0
  assert analyze("Python, APIs REST e Graduação em TI", CRITERIA).score == 100


def test_same_input_gives_same_result():
  text = "Dev Python com APIs REST"
  assert analyze(text, CRITERIA) == analyze(text, CRITERIA)


def test_suggestions_cover_only_missing_criteria_by_weight():
  suggestions = analyze("Experiência com Java", CRITERIA).suggestions
  assert len(suggestions) == 3
  assert "Python" in suggestions[0]
  assert "APIs REST" in suggestions[1]
  assert analyze("Python, APIs REST e Graduação em TI", CRITERIA).suggestions == []


def test_detector_is_only_called_without_keyword_match():
  detector = FakeDetector(0.9)
  analyze("Dev Python", CRITERIA, detector)
  assert detector.calls == ["APIs REST", "Graduação em TI"]


def test_detector_thresholds():
  criterion = [CriterionInput("Liderança", "habilidade", 100)]
  expected = {0.7: CriterionStatus.PRESENT, 0.69: CriterionStatus.REVIEW, 0.31: CriterionStatus.REVIEW, 0.3: CriterionStatus.ABSENT}
  for probability, status in expected.items():
    analysis = analyze("Texto", criterion, FakeDetector(probability))
    assert analysis.results[0].status == status
    assert analysis.results[0].source == "fake"
    assert analysis.results[0].model_version == "fake-1"


def test_review_scores_zero_and_generates_suggestion():
  criterion = [CriterionInput("Liderança", "habilidade", 100)]
  analysis = analyze("Texto", criterion, FakeDetector(0.5))
  assert analysis.score == 0
  assert len(analysis.suggestions) == 1


def test_details_are_json_ready():
  details = analyze("Dev Python", CRITERIA).to_details()
  assert details["algorithm_version"] == "1"
  assert details["criteria"][0]["status"] == "present"
  assert details["criteria"][0]["points"] == 50
  assert "Python" in details["criteria"][0]["evidence"]
