# -*- coding: utf-8 -*-
from collections import OrderedDict

class Item(object):
    def __init__(self, parent=None):
        self.__data__ = {}
        self.__parent__ = parent
        self.__children__ = []

    def append(self, quantity=1):
        self.__children__.append( Item(self) )

    def child(self, row, item=None):
        if type(row) is list:
            child = self
            for r in row:
                child = child.child(r)
            return child
        if item is None:
            if len(self.__children__) == 0:
                return 0
            return self.__children__[row]
        if type(item) is Item:
            self.__children__[row] = item
            return
        return self.__children__[row]

    def child_count(self):
        return len(self.__children__)

    def children(self, row=None, count=None):
        if row is None:
            return self.__children__
        if type(row) is list:
            self.__children__ = row
            return
        return self.__children__[row:row+count]

    def data(self, key=None, value=None):
        if key is None:
            return self.__data__
        if type(key) is dict or type(key) is OrderedDict:
            self.__data__ = key
            return
        if value is None:
            return self.__data__.get(key)
        self.__data__[key] = value

    def delete(self, key):
        del self.__data__[key]

    def extend(self, children):
        self.__children__.extend(children)

    def insert(self, row, count=1):
        self.__children__[row:row] = [ Item(self) for i in range(count) ]

    def move(self, row, count, destination):
        d = self.__children__[row:row+count]
        del self.__children__[row:row+count]
        self.__children__[destination:destination] = d

    def parent(self, item=None):
        if item is None:
            return self.__parent__
        else:
            self.__parent__ = item

    def pop(self, row, count=1):
        d = self.__children__[row:row+count]
        del self.__children__[row:row+count]
        return d

    def remove(self, row, count=1):
        if count == 1:
            del self.__children__[row]
        else:
            del self.__children__[row:row+count]

    def row(self):
        if self.__parent__:
            if self in self.__parent__.children():
                return self.__parent__.children().index(self)
        return 0
