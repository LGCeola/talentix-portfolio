from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from apps.backend.core.exceptions import (
  AcessoNegado,
  ArquivoMuitoGrande,
  Conflito,
  CredenciaisInvalidas,
  FormatoNaoSuportado,
  NaoEncontrado,
  RegraDeNegocioViolada,
  TalentixException,
)

# A classe mais específica vence: o MRO da exceção é percorrido em ordem.
STATUS_BY_EXCEPTION: dict[type[TalentixException], int] = {
  NaoEncontrado: status.HTTP_404_NOT_FOUND,
  CredenciaisInvalidas: status.HTTP_401_UNAUTHORIZED,
  AcessoNegado: status.HTTP_403_FORBIDDEN,
  Conflito: status.HTTP_409_CONFLICT,
  FormatoNaoSuportado: status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
  ArquivoMuitoGrande: status.HTTP_413_CONTENT_TOO_LARGE,
  RegraDeNegocioViolada: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


def status_for(exc: TalentixException) -> int:
  for cls in type(exc).__mro__:
    if cls in STATUS_BY_EXCEPTION:
      return STATUS_BY_EXCEPTION[cls]
  return status.HTTP_400_BAD_REQUEST


async def talentix_exception_handler(request: Request, exc: TalentixException) -> JSONResponse:
  headers = {"WWW-Authenticate": "Bearer"} if isinstance(exc, CredenciaisInvalidas) else None
  # Mesmo formato do HTTPException ({"detail": ...}), para o frontend tratar todos os erros igual.
  return JSONResponse(status_code=status_for(exc), content={"detail": exc.message}, headers=headers)


def register_exception_handlers(app: FastAPI) -> None:
  app.add_exception_handler(TalentixException, talentix_exception_handler)
