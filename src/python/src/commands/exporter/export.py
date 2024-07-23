from typing import List
from sqlalchemy import select, update
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
            ]).where(Project.exported == 0).order_by(Project.id.asc())
        return stmt
    
    def update_results_on_exporting(self, project_ids: List[int]):
        update_stmt = (
            update(Project)
            .where(Project.id.in_(project_ids))
            .values(exported=1)
        )
        d = self.conn.runInteraction(self.update_interaction, update_stmt)
        d.addErrback(self.handle_error)
