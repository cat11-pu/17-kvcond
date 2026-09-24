"""kvstore.py：带版本号的键值存储（基线：只有无条件写）。"""
from __future__ import annotations


class KV:
    def __init__(self):
        self.values = {}
        self.versions = {}
        self.writes = 0

    def get(self, key):
        return self.values.get(key)

    def version(self, key) -> int:
        return self.versions.get(key, 0)

    def put(self, key, value) -> int:
        self.writes += 1
        self.values[key] = value
        self.versions[key] = self.writes
        return self.versions[key]
