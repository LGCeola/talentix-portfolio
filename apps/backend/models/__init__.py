"""Importa todos os modelos para registrar as tabelas nos metadados do SQLAlchemy."""

from apps.backend.models.candidatura import Application, ApplicationStatus
from apps.backend.models.criterio import Criterion, CriterionType
from apps.backend.models.curriculo import Resume
from apps.backend.models.pontuacao import Score
from apps.backend.models.relatorio import Report
from apps.backend.models.usuario import User, UserType
from apps.backend.models.vaga import Vacancy, VacancyStatus

__all__ = ["Application", "ApplicationStatus", "Criterion", "CriterionType", "Resume", "Score", "Report", "User", "UserType", "Vacancy", "VacancyStatus"]
