from typing import Literal

from pydantic import BaseModel, Field


class CandidaturaRequest(BaseModel):
  vacancy_id: int = Field(gt=0)
  resume_id: int = Field(gt=0)
  # O currículo só é compartilhado com o recrutador mediante autorização explícita (LGPD, RFC 6.1).
  consent: Literal[True] = Field(description="Autorização para compartilhar o currículo com o recrutador da vaga")
