from sqlalchemy import select
from commands.abstract import CSVExporter
from database.models import Project


class Exporter(CSVExporter):
    def select_results(self):
        stmt = select([
            Project.id,
            Project.url,
            Project.platform,
            Project.title,
            Project.email,
            Project.website,
            Project.telegram,
            Project.twitter,
            Project.created_at,
            ]).order_by(Project.id.asc())
        return stmt