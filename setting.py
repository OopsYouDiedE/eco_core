import os

import yaml


class IDManager1:

    # 从文件中加载ID
    def __init__(self, file_path='data.yaml'):
        self.file_path = file_path
        self.data = set()
        self.data = self.load_ids()

    def load_ids(self):
        try:
            with open(self.file_path, 'r') as f:
                return yaml.safe_load(f)
        except:
            self.save_ids()
            return self.data

    def save_ids(self):
        with open(self.file_path, 'w') as f:
            yaml.dump(self.data, f)

    # 添加新ID
    def add_id(self, new_id):
        if new_id not in self.data:
            self.data.add(new_id)
            self.save_ids()
        return f'添加id{new_id}'

    # 删除ID
    def remove_id(self, id_to_remove):
        if id_to_remove in self.data:
            self.data.remove(id_to_remove)
            self.save_ids()
            return f'删除id{id_to_remove}'
        else:
            return '无此id，删除失败'
# 物品合成器：['消耗物品':，'生成物品'：，'工具'：]
synthesis_table_manager=IDManager1(f'{os.path.dirname(__file__)}/synthesis_table_manager.yaml')
class IDManager:
    def __init__(self, filename):
        self.filename = filename
        self.ids = self.load_ids()

    # 从文件中加载ID
    def load_ids(self):
        try:
            with open(self.filename, 'r') as file:
                return set(file.read().splitlines())
        except FileNotFoundError:
            return set()

    # 将ID保存到文件
    def save_ids(self):
        with open(self.filename, 'w') as file:
            file.write('\n'.join(self.ids))

    # 添加新ID
    def add_id(self, new_id):
        if new_id not in self.ids:
            self.ids.add(new_id)
            self.save_ids()
        return f'添加id{new_id}'

    # 删除ID
    def remove_id(self, id_to_remove):
        if id_to_remove in self.ids:
            self.ids.remove(id_to_remove)
            self.save_ids()
            return f'删除id{id_to_remove}'
        else:
            return '无此id，删除失败'


# id身份组管理器，和可交换物品管理器。
id_manager = IDManager(f'{os.path.dirname(__file__)}/ids.txt')
exchangeable_item = IDManager(f'{os.path.dirname(__file__)}/exchangeable_item.txt')


class KeyValueManager:
    def __init__(self, file_path='data.yaml'):
        self.file_path = file_path
        self.data = {}
        self.data = self.load_dict()

    def load_dict(self):
        try:
            with open(self.file_path, 'r') as f:
                return yaml.safe_load(f)
        except:
            self.save_dict()
            return self.data

    def save_dict(self):
        with open(self.file_path, 'w') as f:
            yaml.dump(self.data, f)

    def add_kv(self, key, value):
        self.data[key] = value
        self.save_dict()

    def remove_kv(self, key):
        if key in self.data:
            del self.data[key]
            self.save_dict()
        else:
            print("Key not found")


# 货币发行记录，市场管理器，赌场管理器。
coin_and_owner = KeyValueManager(f'{os.path.dirname(__file__)}/coin_and_owner.yaml')
market_manager = KeyValueManager(f'{os.path.dirname(__file__)}/market_manager.yaml')
gambling_manager = KeyValueManager(f'{os.path.dirname(__file__)}/gambling_manager.yaml')

