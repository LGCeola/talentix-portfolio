"""Exceções de domínio do Talentix.

Os services lançam estas exceções sem conhecer HTTP; a tradução para status code
fica centralizada em core/exception_handlers.py.
"""


class TalentixException(Exception):
  """Exceção base da aplicação."""
  default_message = "Não foi possível concluir a operação"

  def __init__(self, message: str | None = None):
    self.message = message or self.default_message
    super().__init__(self.message)


# ─── Categorias ───

class NaoEncontrado(TalentixException):
  default_message = "Recurso não encontrado"


class CredenciaisInvalidas(TalentixException):
  default_message = "E-mail ou senha inválidos"


class AcessoNegado(TalentixException):
  default_message = "Você não tem permissão para acessar este recurso"


class Conflito(TalentixException):
  """A operação conflita com o estado atual do recurso (ex.: vaga encerrada, e-mail em uso)."""
  default_message = "A operação conflita com o estado atual do recurso"


class RegraDeNegocioViolada(TalentixException):
  """Os dados são válidos em formato, mas violam uma regra do sistema (ex.: RN03)."""
  default_message = "Os dados enviados não atendem às regras do sistema"


# ─── Usuários ───

class UsuarioNaoEncontrado(NaoEncontrado):
  default_message = "Usuário não encontrado"


class EmailJaCadastrado(Conflito):
  default_message = "Já existe um usuário cadastrado com este e-mail"


# ─── Currículos ───

class CurriculoNaoEncontrado(NaoEncontrado):
  default_message = "Currículo não encontrado"


class CurriculoInvalido(RegraDeNegocioViolada):
  default_message = "O currículo enviado é inválido"


class FormatoNaoSuportado(CurriculoInvalido):
  default_message = "Formato não suportado. Envie um arquivo PDF ou TXT"


class ArquivoMuitoGrande(CurriculoInvalido):
  default_message = "O arquivo excede o tamanho máximo permitido"


# ─── Vagas e candidaturas ───

class VagaNaoEncontrada(NaoEncontrado):
  default_message = "Vaga não encontrada"


class VagaNaoPublicavel(RegraDeNegocioViolada):
  default_message = "A vaga não atende aos requisitos para publicação"


class CandidaturaNaoEncontrada(NaoEncontrado):
  default_message = "Candidatura não encontrada"


class CandidaturaDuplicada(Conflito):
  default_message = "Você já se candidatou a esta vaga"
