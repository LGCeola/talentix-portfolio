"""Falhas do armazenamento de arquivos: nenhuma deixa dado pela metade nem quebra a exclusão da conta."""
import io
import logging
from types import SimpleNamespace

import pytest

from apps.backend.core.exceptions import CurriculoNaoEncontrado
from apps.backend.core.security import hash_password
from apps.backend.integrations.storage import LocalStorage, StorageError
from apps.backend.services.CandidaturaService import CandidaturaService
from apps.backend.services.CurriculoService import CurriculoService
from apps.backend.services.UsuarioService import UsuarioService


class FailingRepository:
  def create(self, db, resume):
    raise RuntimeError("banco fora do ar")


def test_upload_removes_the_file_when_the_database_fails(tmp_path):
  storage = LocalStorage(tmp_path)
  service = CurriculoService(repository=FailingRepository(), storage=storage)
  candidate = SimpleNamespace(id=7)

  with pytest.raises(RuntimeError):
    service.upload(None, candidate, "cv.txt", io.BytesIO(b"Curriculo ficticio com Python"))

  # O arquivo gravado antes da falha não fica órfão.
  assert not any((tmp_path / "7").iterdir())


class BrokenStorage:
  def read(self, key):
    raise StorageError("chave inválida")

  def delete_prefix(self, prefix):
    raise OSError("sem acesso ao armazenamento")


def test_download_of_an_unreadable_file_returns_not_found():
  application = SimpleNamespace(resume=SimpleNamespace(file_url="../fora.pdf", original_filename="cv.pdf"))
  repository = SimpleNamespace(get_by_id_and_recruiter=lambda db, application_id, recruiter_id: application)
  service = CandidaturaService(repository=repository, detector=object(), storage=BrokenStorage())

  with pytest.raises(CurriculoNaoEncontrado):
    service.received_resume(None, SimpleNamespace(id=1), 10)


def test_account_is_deleted_even_if_the_files_cannot_be_removed(caplog):
  deleted = []
  repository = SimpleNamespace(delete_with_data=lambda db, user: deleted.append(user.id))
  service = UsuarioService(repository=repository, storage=BrokenStorage())
  user = SimpleNamespace(id=7, password_hash=hash_password("senha-teste-123"))

  with caplog.at_level(logging.ERROR):
    service.delete_account(None, user, "senha-teste-123")

  assert deleted == [7]
  assert "Falha ao remover os arquivos da conta excluída" in caplog.text
