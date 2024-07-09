from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import JSON

from database.models import Base
from .mixins import MysqlPrimaryKeyMixin, MysqlStatusMixin, MysqlTimestampsMixin

STR_768 = 768

class Project(Base, MysqlPrimaryKeyMixin, MysqlStatusMixin, MysqlTimestampsMixin):
    __tablename__ = 'project'
    
    project_id = Column(String(STR_768), nullable=False, unique=True)
    url = Column("url", String(STR_768), unique=True, nullable=False)
    domain = Column('domain', String(255), nullable=False)
    platform = Column('platform', String(255), nullable=False)
    title = Column('title', String(255), nullable=False)
    website = Column(String(STR_768), nullable=True)
    contact = Column(JSON, nullable=True)
