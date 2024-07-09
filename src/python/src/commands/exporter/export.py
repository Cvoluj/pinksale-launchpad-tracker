from sqlalchemy import select
from commands.abstract import CSVExporter
from database.models import Project


class Exporter(CSVExporter):
    def select_results(self):
        stmt = select(Project).order_by(Project.id.asc())
        return stmt