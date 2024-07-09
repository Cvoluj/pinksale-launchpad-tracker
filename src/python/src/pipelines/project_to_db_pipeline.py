from sqlalchemy.dialects.mysql import insert, Insert
from MySQLdb.cursors import DictCursor
from utils.logger_mixin import LoggerMixin
from twisted.enterprise.adbapi import ConnectionPool
from scrapy.utils.project import get_project_settings
from rmq.utils.sql_expressions import compile_expression

from database.models import Project

class ProjectToDatabasePipeline(LoggerMixin):

    def open_spider(self, spider):
        settings = get_project_settings()
        self.conn = ConnectionPool(
                "MySQLdb",
                host=settings.get("DB_HOST"),
                port=settings.get("DB_PORT"),
                user=settings.get("DB_USERNAME"),
                passwd=str(settings.get("DB_PASSWORD")),
                db=settings.get("DB_DATABASE"),
                cursorclass=DictCursor,
                charset="utf8mb4",
                cp_reconnect=True,
            )
        
    def process_item(self, item, spider):
        query: Insert = insert(Project).values(**item).on_duplicate_key_update(**item)
        d = self.conn.runQuery(*compile_expression(query))
        d.addCallback(self.handle_process_item)
        d.addErrback(self.handle_error, item, spider)
            
    def handle_process_item(self, _):
        pass

    def handle_error(self, failure, item, spider):
        self.logger.error(f"Error {failure} processing item: {item} ")
        
    def close_spider(self, spider):
        self.conn.close()