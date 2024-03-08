import sqlite3
import sys
from random import randint
from . import database_manager

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


def sell(seller_id, item, quantity, exchange_item, exchange_quantity):
  """卖家使用此函数来发布销售信息"""
  seller_id = str(seller_id)  # 确保ID是字符串
  # 生成一个随机ID
  sale_id = str(randint(1000, sys.maxsize))
  # 将销售信息插入到数据库
  cursor.execute(
      '''
    INSERT INTO sales (id, seller_id, item, quantity, exchange_item, exchange_quantity)
    VALUES (?, ?, ?, ?, ?, ?)
    ''',
      (sale_id, seller_id, item, quantity, exchange_item, exchange_quantity))
  conn.commit()
  return sale_id


def buy(buyer_id, sale_id):
  """买家使用此函数来执行购买"""
  buyer_id = str(buyer_id)  # 确保ID是字符串
  # 从数据库中获取销售信息
  cursor.execute('SELECT * FROM sales WHERE id=?', (sale_id, ))
  sale = cursor.fetchone()
  if sale:
    sale_id, seller_id, item, quantity, exchange_item, exchange_quantity = sale
    # 检查买家和卖家是否有足够物品
    if database_manager.query_item(
        buyer_id,
        exchange_item)[2] >= exchange_quantity and database_manager.query_item(
            seller_id, item)[2] >= quantity:
      # 更新买家和卖家的物品数量
      database_manager.update_item(buyer_id, exchange_item, -exchange_quantity)
      database_manager.update_item(seller_id, item, -quantity)
      database_manager.update_item(buyer_id, item, quantity)
      database_manager.update_item(seller_id, exchange_item, exchange_quantity)
      # 确认交易后，移除该销售信息
      cursor.execute('DELETE FROM sales WHERE id=?', (sale_id, ))
      conn.commit()
      return(f"交易成功，ID为{sale_id}的销售信息已被移除。")
    else:
      return("交易失败，买家或卖家物品数量不足。")
  else:
    return("交易失败，未找到该ID的销售信息。")
