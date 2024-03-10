import yaml


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
