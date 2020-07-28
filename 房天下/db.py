from sqlalchemy import create_engine
from sqlalchemy import Column,Integer,String,Text
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.ext.declarative import declarative_base

BASE = declarative_base()#创建基类

#此处没有使用pymysql的驱动
#请安装pip install mysql-connector-python
#engine中的 mysqlconnector 为 mysql官网驱动
engine = create_engine(
	"mysql+mysqlconnector://root:root@127.0.0.1:3306/test?charset=utf8",#确定编码格式
	max_overflow = 500,#超过连接池大小外最多可以创建的链接
	pool_size = 100,#连接池大小
	echo = False,#调试信息展示
)

class House(BASE):#继承基类
	__tablename__ = 'house' #表名字
	id = Column(Integer,primary_key = True,autoincrement = True)
	block = Column(String(125))
	title = Column(String(125))
	rent = Column(String(125))
	data = Column(Text())

BASE.metadata.create_all(engine)#通过基类创建表
Session = sessionmaker(engine)
sess = scoped_session(Session)

