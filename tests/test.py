import json
from types import SimpleNamespace


class DotDict(dict):
    """使点语法可用于字典"""
    def __getattr__(self, name):
        value = self[name]
        if isinstance(value, dict):
            return DotDict(value)
        return value


with open("config.json", "r", encoding="utf-8") as f:
    content = f.read()
    content = json.loads(content)


print(content["machine_id"])