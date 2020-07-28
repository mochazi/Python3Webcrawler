from sqlalchemy import Column,Integer,String,create_engine
from sqlalchemy.orm import  sessionmaker,scoped_session
from sqlalchemy.ext.declarative import declarative_base

#此处没有使用pymysql的驱动
#请安装pip install mysql-connector-python
#engine中的 mysqlconnector 为 mysql官网驱动
engine = create_engine('mysql+mysqlconnector://root:root@localhost:3306/test?charset=utf8',
                       max_overflow = 500,#超过连接池大小外最多可以创建的链接
                       pool_size = 100,#连接池大小
                       echo = False,#调试信息展示
)
Base = declarative_base()

class Song(Base):
    __tablename__ = 'song'
    song_id = Column(Integer,primary_key = True,autoincrement = True)
    song_name = Column(String(64))
    song_ablum = Column(String(64))
    song_mid = Column(String(50))
    song_singer = Column(String(50))
Base.metadata.create_all(engine)

DBsession = sessionmaker(bind = engine)

SQLsession = scoped_session(DBsession)





