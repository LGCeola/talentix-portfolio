from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from sqlalchemy.orm import Session

from apps.backend.algorithm.parser import SUPPORTED_EXTENSIONS, ResumeParseError, extract_text
from apps.backend.core.config import settings
from apps.backend.core.exceptions import ArquivoMuitoGrande, Conflito, CurriculoInvalido, CurriculoNaoEncontrado, FormatoNaoSuportado
from apps.backend.models.curriculo import Resume
from apps.backend.models.usuario import User
from apps.backend.repositories.CurriculoRepository import CurriculoRepository


class CurriculoService:
  def __init__(self, repository: CurriculoRepository | None = None, upload_dir: Path | None = None):
    self.repository = repository or CurriculoRepository()
    self.upload_dir = upload_dir or settings.UPLOAD_DIR

  def list_mine(self, db: Session, candidate: User) -> list[Resume]:
    return self.repository.list_by_candidate(db, candidate.id)

  def get_mine(self, db: Session, candidate: User, resume_id: int) -> Resume:
    resume = self.repository.get_by_id_and_candidate(db, resume_id, candidate.id)
    if not resume:
      raise CurriculoNaoEncontrado()
    return resume

  def upload(self, db: Session, candidate: User, filename: str | None, stream: BinaryIO) -> Resume:
    original_filename = Path(filename or "").name
    extension = Path(original_filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
      raise FormatoNaoSuportado()

    max_bytes = settings.MAX_RESUME_SIZE_MB * 1024 * 1024
    content = stream.read(max_bytes + 1)
    if len(content) > max_bytes:
      raise ArquivoMuitoGrande(f"O arquivo excede o limite de {settings.MAX_RESUME_SIZE_MB} MB")
    if not content:
      raise CurriculoInvalido("O arquivo enviado está vazio")

    try:
      text = extract_text(content, extension)
    except ResumeParseError as error:
      raise CurriculoInvalido(str(error)) from error

    # O nome em disco é gerado pelo servidor; o nome original serve apenas para exibição.
    relative_path = Path(str(candidate.id)) / f"{uuid4().hex}{extension}"
    destination = self.upload_dir / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)

    resume = Resume(candidate_id=candidate.id, file_url=relative_path.as_posix(), original_filename=original_filename[:255], extracted_text=text)
    try:
      return self.repository.create(db, resume)
    except Exception:
      destination.unlink(missing_ok=True)
      raise

  def delete(self, db: Session, candidate: User, resume_id: int) -> None:
    resume = self.get_mine(db, candidate, resume_id)
    if self.repository.has_applications(db, resume.id):
      raise Conflito("Este currículo está vinculado a candidaturas e não pode ser excluído")

    file_path = self.upload_dir / resume.file_url
    self.repository.delete(db, resume)
    file_path.unlink(missing_ok=True)
