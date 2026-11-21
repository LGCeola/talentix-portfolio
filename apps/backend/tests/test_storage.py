"""Armazenamento dos currículos: pasta local (desenvolvimento) e Azure Blob Storage (produção)."""
import sys
import types

import pytest
from azure.core.exceptions import ResourceNotFoundError

from apps.backend.core.config import settings
from apps.backend.integrations import storage as storage_module
from apps.backend.integrations.storage import BlobStorage, LocalStorage, StorageError, build_storage


def test_local_storage_saves_reads_and_deletes(tmp_path):
  storage = LocalStorage(tmp_path)
  storage.save("7/a.pdf", b"conteudo")
  assert storage.read("7/a.pdf") == b"conteudo"
  assert storage.read("7/nao-existe.pdf") is None

  storage.delete("7/a.pdf")
  storage.delete("7/a.pdf")  # apagar de novo não é erro
  assert storage.read("7/a.pdf") is None


def test_local_storage_deletes_all_files_of_an_account(tmp_path):
  storage = LocalStorage(tmp_path)
  storage.save("7/a.pdf", b"1")
  storage.save("7/b.txt", b"2")
  storage.save("8/c.pdf", b"3")

  storage.delete_prefix("7")
  storage.delete_prefix("99")  # conta sem arquivos

  assert not (tmp_path / "7").exists()
  assert storage.read("8/c.pdf") == b"3"


@pytest.mark.parametrize("key", ["../fora.pdf", "7/../../fora.pdf", "", "."])
def test_local_storage_refuses_keys_outside_the_upload_folder(tmp_path, key):
  storage = LocalStorage(tmp_path / "uploads")
  with pytest.raises(StorageError):
    storage.read(key)
  with pytest.raises(StorageError):
    storage.save(key, b"x")


class FakeContainer:
  """Imita o ContainerClient do Azure SDK, guardando os blobs num dicionário."""

  def __init__(self):
    self.blobs = {}

  def upload_blob(self, name, data, overwrite):
    assert overwrite is False
    self.blobs[name] = data

  def download_blob(self, name):
    if name not in self.blobs:
      raise ResourceNotFoundError("não encontrado")
    return types.SimpleNamespace(readall=lambda: self.blobs[name])

  def delete_blob(self, name):
    if name not in self.blobs:
      raise ResourceNotFoundError("não encontrado")
    del self.blobs[name]

  def list_blob_names(self, name_starts_with):
    return [name for name in list(self.blobs) if name.startswith(name_starts_with)]


def test_blob_storage_saves_reads_and_deletes():
  container = FakeContainer()
  storage = BlobStorage(container)
  storage.save("7/a.pdf", b"conteudo")
  assert storage.read("7/a.pdf") == b"conteudo"
  assert storage.read("7/nao-existe.pdf") is None

  storage.delete("7/a.pdf")
  storage.delete("7/a.pdf")
  assert container.blobs == {}


def test_blob_storage_deletes_only_the_account_prefix():
  container = FakeContainer()
  storage = BlobStorage(container)
  for key in ("7/a.pdf", "7/b.txt", "70/c.pdf"):
    storage.save(key, b"x")

  storage.delete_prefix("7")

  # "70/" não é apagado junto com "7/".
  assert list(container.blobs) == ["70/c.pdf"]


def test_without_azure_account_uses_the_local_folder(monkeypatch, tmp_path):
  monkeypatch.setattr(settings, "AZURE_STORAGE_ACCOUNT_URL", None)
  monkeypatch.setattr(settings, "UPLOAD_DIR", tmp_path)
  storage = build_storage()
  assert isinstance(storage, LocalStorage)
  assert storage.base_dir == tmp_path


def test_with_azure_account_uses_blob_storage_with_managed_identity(monkeypatch):
  calls = {}

  class FakeService:
    def __init__(self, url, credential):
      calls["url"], calls["credential"] = url, credential

    def get_container_client(self, name):
      calls["container"] = name
      return FakeContainer()

  monkeypatch.setitem(sys.modules, "azure.identity", types.SimpleNamespace(DefaultAzureCredential=lambda: "identidade"))
  monkeypatch.setitem(sys.modules, "azure.storage.blob", types.SimpleNamespace(BlobServiceClient=FakeService))
  monkeypatch.setattr(settings, "AZURE_STORAGE_ACCOUNT_URL", "https://conta.blob.core.windows.net")
  monkeypatch.setattr(settings, "AZURE_STORAGE_CONTAINER", "curriculos")

  storage = build_storage()

  assert isinstance(storage, BlobStorage)
  assert calls == {"url": "https://conta.blob.core.windows.net", "credential": "identidade", "container": "curriculos"}


def test_get_storage_reuses_the_same_instance():
  storage_module.get_storage.cache_clear()
  try:
    assert storage_module.get_storage() is storage_module.get_storage()
  finally:
    storage_module.get_storage.cache_clear()
