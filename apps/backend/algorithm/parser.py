"""Ingestion Engine: extrai e normaliza o texto bruto de currículos em PDF ou texto (RN02)."""

import io
import re

import pdfplumber
from pdfminer.pdfparser import PDFSyntaxError


class ResumeParseError(ValueError):
  pass


SUPPORTED_EXTENSIONS = {".pdf", ".txt"}
_PDF_SIGNATURE = b"%PDF-"


def extract_text(content: bytes, extension: str) -> str:
  if extension == ".pdf":
    text = _extract_pdf(content)
  elif extension == ".txt":
    text = _extract_txt(content)
  else:
    raise ResumeParseError("Formato não suportado. Envie um arquivo PDF ou TXT")

  text = normalize_text(text)
  if not text:
    raise ResumeParseError("Não foi possível extrair texto do currículo. PDFs digitalizados (imagem) não são suportados")
  return text


def normalize_text(text: str) -> str:
  text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
  text = re.sub(r"[ \t\f\v]+", " ", text)
  text = re.sub(r" *\n *", "\n", text)
  text = re.sub(r"\n{3,}", "\n\n", text)
  return text.strip()


def _extract_pdf(content: bytes) -> str:
  if not content.startswith(_PDF_SIGNATURE):
    raise ResumeParseError("O arquivo não é um PDF válido")
  try:
    with pdfplumber.open(io.BytesIO(content)) as pdf:
      return "\n".join(page.extract_text() or "" for page in pdf.pages)
  except (PDFSyntaxError, ValueError) as error:
    raise ResumeParseError("O arquivo PDF está corrompido ou protegido") from error


def _extract_txt(content: bytes) -> str:
  if b"\x00" in content:
    raise ResumeParseError("O arquivo não é um texto válido")
  try:
    return content.decode("utf-8-sig")
  except UnicodeDecodeError:
    return content.decode("latin-1")
