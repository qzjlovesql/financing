import numpy
import pandas as pd
import matplotlib.pylab as pl
import pymysql

conn = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    passwd="123",
    db="financing",
    charset="utf8",
)

# conn = pymysql.connect({
#     "host": "localhost",
#     "port": "3306",
#     "user": "root",
#     "passwd": "123",
#     "db": "financing",
#     "charset": "utf8",
# })

sql = "select * from ftb"
k = pd.read_sql(sql, con=conn)
print(k.describe())
# pl.plot(k)
# pl.xlin(0,10000) #设置横轴范围
# pl.ylin(0,30000) #设置纵轴范围
# pl.show()

