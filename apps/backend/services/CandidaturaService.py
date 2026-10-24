from datetime import datetime, timezone

from sqlalchemy.orm import Session

from apps.backend.core.exceptions import CandidaturaNaoEncontrada, Conflito, CurriculoNaoEncontrado, VagaNaoEncontrada
from apps.backend.models.candidatura import Application, ApplicationStatus
from apps.backend.models.usuario import User
from apps.backend.models.vaga import VacancyStatus
from apps.backend.repositories.CandidaturaRepository import CandidaturaRepository
from apps.backend.repositories.CurriculoRepository import CurriculoRepository
from apps.backend.repositories.VagaRepository import VagaRepository
from apps.backend.schemas.CandidaturaRequest import CandidaturaRequest
from apps.backend.services.VagaService import VagaService


class CandidaturaService:
  def __init__(
    self,
    repository: CandidaturaRepository | None = None,
    vagas: VagaRepository | None = None,
    curriculos: CurriculoRepository | None = None,
    vaga_service: VagaService | None = None,
  ):
    self.repository = repository or CandidaturaRepository()
    self.vagas = vagas or VagaRepository()
    self.curriculos = curriculos or CurriculoRepository()
    self.vaga_service = vaga_service or VagaService()

  def apply(self, db: Session, candidate: User, payload: CandidaturaRequest) -> Application:
    vacancy = self.vagas.get_by_id(db, payload.vacancy_id)
    # Rascunhos são invisíveis para candidatos: responde como se a vaga não existisse.
    if not vacancy or vacancy.status == VacancyStatus.DRAFT:
      raise VagaNaoEncontrada()
    if vacancy.status == VacancyStatus.CLOSED:
      raise Conflito("Esta vaga não está mais recebendo candidaturas")

    if not self.curriculos.get_by_id_and_candidate(db, payload.resume_id, candidate.id):
      raise CurriculoNaoEncontrado()

    application = Application(
      candidate_id=candidate.id,
      vacancy_id=vacancy.id,
      resume_id=payload.resume_id,
      consent_at=datetime.now(timezone.utc),
    )
    return self.repository.create(db, application)

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
