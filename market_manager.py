import sqlite3

# 连接到SQLite数据库
# 数据库文件是market.db
conn = sqlite3.connect('market.db')
cursor = conn.cursor()

# 创建一个表格用于存储销售信息，包括卖家ID
cursor.execute('''
CREATE TABLE IF NOT EXISTS sales (
    id TEXT PRIMARY KEY,
    seller_id TEXT NOT NULL,
    item TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    exchange_item TEXT NOT NULL,
    exchange_quantity INTEGER NOT NULL
)
''')

# 提交事务
conn.commit()
