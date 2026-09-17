class TalentixException(Exception):
  """Exceção base da aplicação."""
  pass


class UsuarioNaoEncontrado(TalentixException):
  pass


class CredenciaisInvalidas(TalentixException):
  pass


class AcessoNegado(TalentixException):
  pass


class CurriculoNaoEncontrado(TalentixException):
  pass


class CurriculoInvalido(TalentixException):
  pass


class VagaNaoEncontrada(TalentixException):
  pass


class CandidaturaNaoEncontrada(TalentixException):
  pass