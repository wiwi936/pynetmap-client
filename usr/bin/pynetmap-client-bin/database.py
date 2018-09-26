#!/usr/bin/env python
__author__ = 'Samir KHERRAZ'
__copyright__ = '(c) Samir HERRAZ 2018-2018'
__version__ = '1.1.0'
__licence__ = 'GPLv3'

from threading import Lock
from table import Table


class Database:
    def __init__(self, ui):
        self.lock = Lock()
        self.tables = dict()
        self.ui = ui
        self.api = self.ui.api
        self.register_table("schema")
        self.register_table("structure")
        self.register_table("base")
        self.register_table("alert")
        self.register_table("module")

    def refresh(self):
        with self.lock:
            for name in self.tables:
                self.tables[name].set_data(self.api.get_table(name))
        self.ui.refresh()

    def cleanup(self):
        self.api.cleanup()

    def register_table(self, name):
        self.tables[name] = Table(name)
        self.tables[name].set_data(self.api.get_table(name))

    def get_table(self, name):
        try:
            return self.tables[name].get_data()
        except:
            return self.api.get_table(name)

    def set_table(self, name, data):
        self.api.set_table(name, data)
        self.refresh()

    def create(self, parent_id=None, newid=None):
        return self.api.create(parent_id, newid)

    def get(self, table, key):
        try:
            return self.tables[table].get(key)
        except:
            return self.api.get(table, key)

    def set(self, table, key, value):
        self.api.set(table, key, value)
        self.refresh()

    def set_attr(self, table, id, key, value):

        self.api.set_attr(table, id, key, value)
        self.refresh()

    def get_attr(self, table, id, key):
        try:
            return self.tables[table].get_attr(id, key)
        except:
            return self.api.get_attr(table, id, key)

    def delete(self, parent_id, newid):
        self.api.delete(parent_id, newid)
        self.refresh()

    def move(self, id, newparent):
        self.api.move(id, newparent)
        self.refresh()

    def get_children(self, id, lst=None):
        if lst == None:
            lst = self.tables["structure"].get_data()

        for key in lst.keys():
            if key == id:
                return lst[key]
            else:
                out = self.get_children(id, lst[key])
                if out != None:
                    return out

        return None

    def find_by_attr(self,  id, attr=None):
        out = []
        for key in self.get_table("base"):
            if attr != None:
                if str(self.tables["base"].get(key)[attr]).upper() == str(id).upper():
                    out.append(key)
            for value in self.tables["base"].get(key):
                if str(self.tables["base"].get(key)[value]).upper() == str(id).upper():
                    out.append(key)
        return out

    def find_by_schema(self, schema):
        out = []
        for key in self.get_table("base"):
            if str(self.tables["base"].get(key)["base.core.schema"]).upper() == str(schema).upper():
                out.append(key)

        return out

    def find_parent(self, id, lst=None):
        try:
            path = self.find_path(id)
            return path[len(path)-2]
        except:
            return None

    def find_path(self, id, lst=None):
        out = []
        if lst == None:
            lst = self.tables["structure"].get_data()

        for key in lst.keys():
            key = str(key)
            if key == id:
                out.append(id)
                return out
            else:
                res = self.find_path(id, lst[key])
                if len(res) > 0:
                    out.append(key)
                    out += res

        return out
