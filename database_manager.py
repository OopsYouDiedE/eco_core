import sqlite3

# 连接数据库
conn = sqlite3.connect(f'{os.path.dirname(__file__)}/core.db')
# 创建游标对象
cur = conn.cursor()

# 创建表，如果不存在的话
cur.execute('''
CREATE TABLE IF NOT EXISTS items (
    uid TEXT,
    item TEXT,
    quantity INTEGER,
    PRIMARY KEY (uid, item)
)
''')


# 定义一个函数，修改用户的物品数量
def update_item(user_id, item, quantity, in_add_mode=True):
    # 查询表中是否存在该用户和物品的记录
    uid = str(user_id)
    cur.execute(
        '''
      SELECT * FROM items
      WHERE uid = ? AND item = ?
      ''', (uid, item))
    # 获取查询结果
    result = cur.fetchone()
    # 如果结果为空，说明表中不存在该记录，需要插入一条新的记录
    if result is None:
        cur.execute(
            '''
            INSERT INTO items (uid, item, quantity)
            VALUES (?, ?, ?)
            ''', (uid, item, quantity))
    # 如果结果不为空，说明表中已经存在该记录，需要更新数量
    else:
        if in_add_mode:
            cur.execute(
                '''
                  UPDATE items
                  SET quantity = quantity+ ?
                  WHERE uid = ? AND item = ?
                  ''', (quantity, uid, item))
        else:
            cur.execute(
                '''
                  UPDATE items
                  SET quantity = ?
                  WHERE uid = ? AND item = ?
                  ''', (quantity, uid, item))
    # 提交更改
    conn.commit()


# 定义一个函数，根据用户id查询物品数量和总和
def query_item(user_id, item):
    uid = str(user_id)
    # 查询表中该用户拥有的所有物品的数量
    cur.execute(
        '''
          SELECT * FROM items
          WHERE uid = ? AND item = ?
          ''', (uid, item))
    # 获取查询结果
    result = cur.fetchone()
    if result:
        return result
    else:
        return (uid, item, 0)


def get_items_by_uid(uid: str):
    uid = str(uid)
    # 查询指定uid的所有非零数量物品
    cur.execute('SELECT item, quantity FROM items WHERE uid = ? AND quantity > 0', (uid,))

    # 获取查询结果
    items = cur.fetchall()
    return str(items)


def delete_all_data():
    # 连接到数据库
    conn = sqlite3.connect('core.db')
    cur = conn.cursor()

    # 删除所有数据
    cur.execute('DELETE FROM items')


def get_all_records():
    # 连接到数据库
    conn = sqlite3.connect('core.db')
    cur = conn.cursor()

    # 查询所有记录
    cur.execute('SELECT * FROM items')

    # 获取查询结果
    records = cur.fetchall()
    return str(records)
