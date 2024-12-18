class BaseConfig(object):
    # 数据库的配置
    DIALCT = "mysql"  # 数据库类型
    DRITVER = "pymysql"  # MySQL 驱动
    HOST = '127.0.0.1'  # 数据库的地址，127.0.0.1 表示本地服务器
    PORT = "3306"  # MySQL 默认端口
    USERNAME = "porter"  # 数据库用户名
    PASSWORD = "qwe123.."  # 数据库密码
    DBNAME = 'web'  # 数据库名称

    # Redis 配置
    REDIS_HOST = '127.0.0.1'  # Redis 地址
    REDIS_PORT = 6379  # Redis 默认端口

    # SQLAlchemy 数据库 URI
    SQLALCHEMY_DATABASE_URI = f"{DIALCT}+{DRITVER}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?charset=utf8"
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # 是否追踪对象的修改
