from datetime import datetime

from pydantic import BaseModel


class CurriculoResponse(BaseModel):
  id: int
  original_filename: str
  updated_at: datetime

  model_config = {"from_attributes": True}


class CurriculoDetailResponse(CurriculoResponse):
  extracted_text: str
