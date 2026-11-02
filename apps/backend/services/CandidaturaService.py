from datetime import datetime, timezone

from sqlalchemy.orm import Session

from apps.backend.algorithm.analyzer import Analysis, SemanticDetector, analyze
from apps.backend.algorithm.score_calculator import CriterionInput
from apps.backend.core.exceptions import CandidaturaNaoEncontrada, Conflito, CurriculoNaoEncontrado, VagaNaoEncontrada
from apps.backend.models.candidatura import Application, ApplicationStatus
from apps.backend.models.curriculo import Resume
from apps.backend.models.usuario import User
from apps.backend.models.vaga import Vacancy, VacancyStatus
from apps.backend.repositories.CandidaturaRepository import CandidaturaRepository
from apps.backend.repositories.CurriculoRepository import CurriculoRepository
from apps.backend.repositories.VagaRepository import VagaRepository
from apps.backend.schemas.CandidaturaRequest import CandidaturaRequest
from apps.backend.schemas.CandidaturaResponse import CompatibilidadeResponse
from apps.backend.services.VagaService import VagaService


class CandidaturaService:
  def __init__(
    self,
    repository: CandidaturaRepository | None = None,
    vagas: VagaRepository | None = None,
    curriculos: CurriculoRepository | None = None,
    vaga_service: VagaService | None = None,
    detector: SemanticDetector | None = None,
  ):
    self.repository = repository or CandidaturaRepository()
    self.vagas = vagas or VagaRepository()
    self.curriculos = curriculos or CurriculoRepository()
    self.vaga_service = vaga_service or VagaService()
    self.detector = detector

  def apply(self, db: Session, candidate: User, payload: CandidaturaRequest) -> Application:
    vacancy = self.vagas.get_by_id(db, payload.vacancy_id)
    # Rascunhos são invisíveis para candidatos: responde como se a vaga não existisse.
    if not vacancy or vacancy.status == VacancyStatus.DRAFT:
      raise VagaNaoEncontrada()
    if vacancy.status == VacancyStatus.CLOSED:
      raise Conflito("Esta vaga não está mais recebendo candidaturas")

    resume = self._get_resume(db, candidate, payload.resume_id)
    analysis = self._analyze(vacancy, resume, self.detector)

    application = Application(
      candidate_id=candidate.id,
      vacancy_id=vacancy.id,
      resume_id=resume.id,
      consent_at=datetime.now(timezone.utc),
      overall_score=analysis.score,
      score_details=analysis.to_details(),
      improvement_suggestions="\n".join(analysis.suggestions),
    )
    return self.repository.create(db, application)

  def compatibility(self, db: Session, candidate: User, vacancy_id: int, resume_id: int) -> CompatibilidadeResponse:
    vacancy = self.vaga_service.get_visible(db, candidate, vacancy_id)
    resume = self._get_resume(db, candidate, resume_id)
    # Sem detector externo: antes da candidatura não há consentimento para enviar o currículo a terceiros.
    analysis = self._analyze(vacancy, resume, None)
    return CompatibilidadeResponse(score=analysis.score, criteria=analysis.to_details()["criteria"], suggestions=analysis.suggestions)

  def list_mine(self, db: Session, candidate: User) -> list[Application]:
    return self.repository.list_by_candidate(db, candidate.id)

  def withdraw(self, db: Session, candidate: User, application_id: int) -> None:
    application = self.repository.get_by_id_and_candidate(db, application_id, candidate.id)
    if not application:
      raise CandidaturaNaoEncontrada()
    if application.status != ApplicationStatus.PENDING:
      raise Conflito("Candidaturas já avaliadas pelo recrutador não podem ser retiradas")
    self.repository.delete(db, application)

  def list_received(self, db: Session, recruiter: User, vacancy_id: int) -> list[Application]:
    vacancy = self.vaga_service.get_mine(db, recruiter, vacancy_id)
    return self.repository.list_by_vacancy(db, vacancy.id)

  def _get_resume(self, db: Session, candidate: User, resume_id: int) -> Resume:
    resume = self.curriculos.get_by_id_and_candidate(db, resume_id, candidate.id)
    if not resume:
      raise CurriculoNaoEncontrado()
    return resume

  def _analyze(self, vacancy: Vacancy, resume: Resume, detector: SemanticDetector | None) -> Analysis:
    criteria = [
      CriterionInput(name=criterion.name, criterion_type=criterion.criterion_type.value, weight=criterion.weight)
      for criterion in sorted(vacancy.criteria, key=lambda item: item.id)
    ]
    return analyze(resume.extracted_text, criteria, detector)
