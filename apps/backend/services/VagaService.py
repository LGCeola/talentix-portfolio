from sqlalchemy.orm import Session

from apps.backend.core.exceptions import Conflito, VagaNaoEncontrada, VagaNaoPublicavel
from apps.backend.models.criterio import Criterion
from apps.backend.models.usuario import User, UserType
from apps.backend.models.vaga import Vacancy, VacancyStatus
from apps.backend.repositories.CandidaturaRepository import CandidaturaRepository
from apps.backend.repositories.VagaRepository import VagaRepository
from apps.backend.schemas.VagaRequest import VagaRequest
from apps.backend.schemas.VagaResponse import CriterioResponse, VagaPublicaResponse, VagaResumoResponse


class VagaService:
  def __init__(self, repository: VagaRepository | None = None, candidaturas: CandidaturaRepository | None = None):
    self.repository = repository or VagaRepository()
    self.candidaturas = candidaturas or CandidaturaRepository()

  def list_open(self, db: Session, candidate: User) -> list[VagaPublicaResponse]:
    applied = self.candidaturas.vacancy_ids_applied_by(db, candidate.id)
    return [
      VagaPublicaResponse(
        id=vacancy.id,
        title=vacancy.title,
        description=vacancy.description,
        created_at=vacancy.created_at,
        criteria=[CriterioResponse.model_validate(criterion) for criterion in vacancy.criteria],
        already_applied=vacancy.id in applied,
      )
      for vacancy in self.repository.list_open(db)
    ]

  def get_visible(self, db: Session, user: User, vacancy_id: int) -> Vacancy:
    """Recrutadores veem as próprias vagas em qualquer status; candidatos, apenas vagas publicadas."""
    if user.user_type == UserType.RECRUITER:
      return self.get_mine(db, user, vacancy_id)
    vacancy = self.repository.get_by_id(db, vacancy_id)
    if not vacancy or vacancy.status != VacancyStatus.OPEN:
      raise VagaNaoEncontrada()
    return vacancy

  def list_mine(self, db: Session, recruiter: User) -> list[VagaResumoResponse]:
    return [
      VagaResumoResponse(
        id=vacancy.id,
        title=vacancy.title,
        status=vacancy.status,
        created_at=vacancy.created_at,
        criteria_count=len(vacancy.criteria),
        applications_count=applications_count,
      )
      for vacancy, applications_count in self.repository.list_by_recruiter_with_counts(db, recruiter.id)
    ]

  def get_mine(self, db: Session, recruiter: User, vacancy_id: int) -> Vacancy:
    vacancy = self.repository.get_by_id_and_recruiter(db, vacancy_id, recruiter.id)
    if not vacancy:
      raise VagaNaoEncontrada()
    return vacancy

  def create(self, db: Session, recruiter: User, payload: VagaRequest) -> Vacancy:
    vacancy = Vacancy(recruiter_id=recruiter.id)
    self._apply(vacancy, payload)
    return self.repository.save(db, vacancy)

  def update(self, db: Session, recruiter: User, vacancy_id: int, payload: VagaRequest) -> Vacancy:
    vacancy = self.get_mine(db, recruiter, vacancy_id)
    if vacancy.status == VacancyStatus.CLOSED:
      raise Conflito("Vagas encerradas não podem ser editadas")
    # Alterar critérios depois de receber candidatos mudaria a base de comparação do ranking.
    if self.repository.has_applications(db, vacancy.id):
      raise Conflito("Esta vaga já recebeu candidaturas e não pode mais ser editada")
    self._apply(vacancy, payload)
    return self.repository.save(db, vacancy)

  def change_status(self, db: Session, recruiter: User, vacancy_id: int, new_status: VacancyStatus) -> Vacancy:
    vacancy = self.get_mine(db, recruiter, vacancy_id)
    if vacancy.status == new_status:
      return vacancy
    if new_status == VacancyStatus.OPEN:
      self._ensure_publishable(vacancy.description, vacancy.criteria)
    elif vacancy.status == VacancyStatus.DRAFT:
      raise Conflito("Rascunhos não podem ser encerrados; exclua a vaga se não for utilizá-la")
    vacancy.status = new_status
    return self.repository.save(db, vacancy)

  def delete(self, db: Session, recruiter: User, vacancy_id: int) -> None:
    vacancy = self.get_mine(db, recruiter, vacancy_id)
    if vacancy.status != VacancyStatus.DRAFT:
      raise Conflito("Apenas rascunhos podem ser excluídos; encerre a vaga para retirá-la do ar")
    self.repository.delete(db, vacancy)

  def _apply(self, vacancy: Vacancy, payload: VagaRequest) -> None:
    if payload.status == VacancyStatus.OPEN:
      self._ensure_publishable(payload.description, payload.criteria)
    vacancy.title = payload.title
    vacancy.description = payload.description
    vacancy.status = payload.status
    vacancy.criteria = [Criterion(name=item.name, criterion_type=item.criterion_type, weight=item.weight) for item in payload.criteria]

  def _ensure_publishable(self, description: str, criteria: list) -> None:
    if not description:
      raise VagaNaoPublicavel("Informe a descrição da vaga antes de publicá-la")
    if not criteria:
      raise VagaNaoPublicavel("A vaga precisa de pelo menos um critério de avaliação")
    total = sum(criterion.weight for criterion in criteria)
    if total != 100:
      raise VagaNaoPublicavel(f"A soma dos pesos deve ser 100% para publicar (atual: {total}%)")
