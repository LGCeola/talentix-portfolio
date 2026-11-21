"""Armazenamento dos arquivos de currículo.

Em desenvolvimento e nos testes, os arquivos ficam numa pasta local (UPLOAD_DIR). Em produção, o disco do
contêiner é apagado a cada nova versão, então os arquivos vão para o Azure Blob Storage, acessado pela
identidade gerenciada do contêiner, sem senha guardada na aplicação.

As chaves seguem o formato "<id do candidato>/<nome gerado>.pdf": o prefixo do candidato permite apagar
todos os arquivos de uma conta excluída (LGPD, RFC 6.1).
"""
import shutil
from functools import cache
from pathlib import Path
from typing import Protocol

from apps.backend.core.config import settings


class StorageError(Exception):
  pass


class ResumeStorage(Protocol):
  def save(self, key: str, content: bytes) -> None: ...

  def read(self, key: str) -> bytes | None: ...

  def delete(self, key: str) -> None: ...

  def delete_prefix(self, prefix: str) -> None: ...


class LocalStorage:
  def __init__(self, base_dir: Path):
    self.base_dir = Path(base_dir)

  def _path(self, key: str) -> Path:
    base = self.base_dir.resolve()
    path = (base / key).resolve()
    # As chaves são geradas pelo servidor, mas a checagem impede ler ou apagar fora da pasta de uploads.
    if not path.is_relative_to(base) or path == base:
      raise StorageError(f"Chave de arquivo inválida: {key!r}")
    return path

  def save(self, key: str, content: bytes) -> None:
    path = self._path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)

  def read(self, key: str) -> bytes | None:
    path = self._path(key)
    return path.read_bytes() if path.is_file() else None

  def delete(self, key: str) -> None:
    self._path(key).unlink(missing_ok=True)

  def delete_prefix(self, prefix: str) -> None:
    path = self._path(prefix)
    if path.is_dir():
      shutil.rmtree(path)


class BlobStorage:
  def __init__(self, container):
    # container: azure.storage.blob.ContainerClient (recebido pronto para facilitar os testes).
    self.container = container

  def save(self, key: str, content: bytes) -> None:
    self.container.upload_blob(name=key, data=content, overwrite=False)

  def read(self, key: str) -> bytes | None:
    from azure.core.exceptions import ResourceNotFoundError

    try:
      return self.container.download_blob(key).readall()
    except ResourceNotFoundError:
      return None

  def delete(self, key: str) -> None:
    from azure.core.exceptions import ResourceNotFoundError

    try:
      self.container.delete_blob(key)
    except ResourceNotFoundError:
      pass

  def delete_prefix(self, prefix: str) -> None:
    for name in self.container.list_blob_names(name_starts_with=f"{prefix.rstrip('/')}/"):
      self.delete(name)


@cache
def get_storage() -> ResumeStorage:
  """Uma instância para toda a aplicação, criada no primeiro uso."""
  return build_storage()


def build_storage() -> ResumeStorage:
  """Blob Storage quando AZURE_STORAGE_ACCOUNT_URL está configurada (produção); senão, a pasta local."""
  if not settings.AZURE_STORAGE_ACCOUNT_URL:
    return LocalStorage(settings.UPLOAD_DIR)

  from azure.identity import DefaultAzureCredential
  from azure.storage.blob import BlobServiceClient

  service = BlobServiceClient(settings.AZURE_STORAGE_ACCOUNT_URL, credential=DefaultAzureCredential())
  return BlobStorage(service.get_container_client(settings.AZURE_STORAGE_CONTAINER))
