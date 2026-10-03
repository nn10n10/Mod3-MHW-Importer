# -*- coding: utf-8 -*-
"""
Created on Sat Feb  9 00:55:14 2019

@author: AsteriskAmpersand
"""

class FileLike():
    def __init__(self, dataArray):
        self.i = 0
        self.data = dataArray
        
    def read(self, x=None):
        if x is None:
            data = self.data[self.i:]
            self.i = len(self.data)
            return data
        if self.i+x > len(self.data):
            raise IndexError("Reading out of Bounds at %d for %d"%(self.i,x))
        if x < 0:
            raise ValueError("Will not read backwards")
        data = self.data[self.i:self.i+x]
        self.seek(self.i + x)
        return data
    
    def seek(self, x):
        if not 0 <= x <= len(self.data):
            raise IndexError("Seek outside file bounds")
        self.i = x
        return
    
    def skip(self, x):
        self.seek(self.i + x)
        return
    
    def tell(self):
        return self.i
    
    def __len__(self):
        return len(self.data)