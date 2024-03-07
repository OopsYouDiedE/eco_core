import sqlite3

# 连接数据库
conn = sqlite3.connect('core_data.db')
# 创建游标对象
cur = conn.cursor()

# 创建表，如果不存在的话
cur.execute('''
CREATE TABLE IF NOT EXISTS items (
    user_id TEXT,
    item TEXT,
    quantity REAL,
    PRIMARY KEY (user_id, item)
)
''')


# 定义一个函数，修改用户的物品数量
def update_item(user_id, item, quantity, in_add_mode=True):
    # 查询表中是否存在该用户和物品的记录
    cur.execute('''
    SELECT * FROM items
    WHERE user_id = ? AND item = ?
    ''', (user_id, item))
    # 获取查询结果
    result = cur.fetchone()
    # 如果结果为空，说明表中不存在该记录，需要插入一条新的记录
    if result is None:
        cur.execute('''
        INSERT INTO items (user_id, item, quantity)
        VALUES (?, ?, ?)
        ''', (user_id, item, quantity))
    # 如果结果不为空，说明表中已经存在该记录，需要更新数量
    else:
        if in_add_mode:
            cur.execute('''
            UPDATE items
            SET quantity = quantity+ ?
            WHERE user_id = ? AND item = ?
            ''', (quantity, user_id, item))
        else:
            cur.execute('''
            UPDATE items
            SET quantity = ?
            WHERE user_id = ? AND item = ?
            ''', (quantity, user_id, item))
    # 提交更改
    conn.commit()

# 定义一个函数，根据用户id查询物品数量和总和
def query_item(user_id,item):
    # 查询表中该用户拥有的所有物品的数量
    cur.execute('''
        SELECT * FROM items
        WHERE user_id = ? AND item = ?
        ''', (user_id, item))
    # 获取查询结果
    result = cur.fetchone()
    print(result)
