# -*- coding: utf-8 -*-

class Column():
    def __init__(self, columns=[]):
        self.__data__ = columns

    def append(self, column=''):
        self.__data__.append(column)

    def count(self):
        return len(self.__data__)

    def data(self, column=None, value=None):
        if column is None:
            return self.__data__
        if value is None:
            if len(self.__data__) <= column or len(self.__data__) <= 0:
                return None
            return self.__data__[column]
        self.__data__[column] = value

    def extend(self, columns):
        self.__data__.extend(columns)

    def index(self, value):
        if value in self.__data__:
            return self.__data__.index(value)
        return None
        
    def insert(self, column, count=1):
        self.__data__[column:column] = [ '' for i in range(count) ]

    def remove(self, column, count=1):
        del self.__data__[column:column+count]
