import pymysql

pymysql.install_as_MySQLdb()

# Monkey patch MySQLdb version to satisfy Django requirements
pymysql.version_info = (2, 2, 4, 'final', 0)
