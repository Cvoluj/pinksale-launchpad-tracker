from sqlalchemy import Column, String

from database.models import Base
from .mixins import MysqlPrimaryKeyMixin, MysqlTimestampsMixin

STR_768 = 768

class Project(Base, MysqlPrimaryKeyMixin, MysqlTimestampsMixin):
    __tablename__ = 'project'
    
    project_id = Column(String(STR_768), nullable=False, unique=True)
    url = Column("url", String(STR_768), unique=True, nullable=False)
    platform = Column('platform', String(255), nullable=False)
    title = Column('title', String(255), nullable=False)
    email = Column('email', String(255), nullable=True)
    website = Column('website', String(STR_768), nullable=True)
    telegram = Column('telegram', String(STR_768), nullable=True)
    twitter = Column('twitter', String(STR_768), nullable=True)

