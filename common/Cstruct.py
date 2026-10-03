# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 13:38:38 2019

@author: AsteriskAmpersand
"""
import struct
from copy import deepcopy
from collections import OrderedDict
from binascii import hexlify

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def HalfToFloat(h):
    return struct.unpack('<e', struct.pack('<H', h))[0]


def minifloatDeserialize(x):
    return struct.unpack('<e', x)[0]


def minifloatSerialize(x):
    return struct.pack('<e', x)


class PyCStruct():
    def __init__(self, data = None, **kwargs):
        self.CStruct = Cstruct(self.fields)
        if data != None:
            self.marshall(data)
        elif kwargs:
            fieldskeys = set(self.fields.keys())
            entrykeys=set(kwargs.keys())
            if fieldskeys == entrykeys:
                [self.__setattr__(attr, value) for attr, value in kwargs.items()]
            else:
                if fieldskeys > entrykeys:
                    raise AttributeError("Missing fields to Initialize")
                if fieldskeys < entrykeys:
                    raise AttributeError("Excessive Fields passed")
                raise AttributeError("Field Mismatch")
        
    def __len__(self):
        return len(self.CStruct)
                
    def marshall(self,data):
        [self.__setattr__(attr, value) for attr, value in self.CStruct.marshall(data).items()]
        
    def serialize(self):
        return self.CStruct.serialize({key:self.__getattribute__(key) for key in self.fields})
    
    def __eq__(self, other):
        return all([self.__getattribute__(key)==other.__getattribute__(key) for key in self.fields])

    defaultProperties = {}
    requiredProperties = {}
    def construct(self,data):
        for field in self.fields:
            if field in data:
                self.__setattr__(field,data[field])
            elif field in self.defaultProperties:
                self.__setattr__(field,deepcopy(self.defaultProperties[field]))
            elif field in self.requiredProperties:
                raise KeyError("Required Property missing in supplied data")
            else:
                self.__setattr__(field,None)
                
    def verify(self):
        for attr in self.fields:
            if self.__getattribute__(attr) is None:
                raise AssertionError("Attribute %s is not initialized."%attr)
                
    def __repr__(self):
        return str({field:(getattr(self,field) if hasattr(self,field) else None) for field in self.fields})

class Cstruct():
    deserializer = lambda y: {'deserializer':lambda x: struct.unpack('<'+y,x)[0], 'serializer': lambda x: struct.pack('<'+y,x)}
    CTypes = {"byte":       {'size':1,**deserializer('b')},
                "int8":     {'size':1,**deserializer('b')},
                "ubyte":    {'size':1,**deserializer('B')},
                "uint8":    {'size':1,**deserializer('B')},
                "short":    {'size':2,**deserializer('h')},
                "int16":    {'size':2,**deserializer('h')},
                "ushort":   {'size':2,**deserializer('H')},
                "uint16":   {'size':2,**deserializer('H')},
                "long":     {'size':4,**deserializer('i')},
                "int32":    {'size':4,**deserializer('i')},
                "int":      {'size':4,**deserializer('i')},
                "ulong":    {'size':4,**deserializer('I')},
                "uint32":   {'size':4,**deserializer('I')},
                "uint":     {'size':4,**deserializer('I')},
                "quad":     {'size':8,**deserializer('q')},
                "int64":    {'size':8,**deserializer('q')},
                "uquad":    {'size':8,**deserializer('Q')},
                "uint64":   {'size':8,**deserializer('Q')},
                "hfloat":   {'size':2,'deserializer':minifloatDeserialize, 'serializer':minifloatSerialize},
                "float":    {'size':4,**deserializer('f')},
                "double":   {'size':8,**deserializer('d')},
                "char":     {'size':1,**deserializer('c')},
                "bool":     {'size':1,**deserializer('b')},
            }
    StructTypes = {}
    
    @staticmethod
    def isArrayType(typeStr):
        return '[' in typeStr and (typeStr[:typeStr.index('[')] in Cstruct.CTypes or typeStr[:typeStr.index('[')] in Cstruct.StructTypes)
        
    @staticmethod
    def arrayType(typeStr):
        base = typeStr[:typeStr.index('[')]
        size = typeStr[typeStr.index('[')+1:typeStr.index(']')]
        #baseTypeCall = Cstruct.CTypes if base in Cstruct.CTypes else Cstruct.StructTypes
        baseTypeCall = Cstruct.CTypes
        
        intSize = int(size)
        return {
                'size': intSize*baseTypeCall[base]['size'], 
                'deserializer': lambda x: [baseTypeCall[base]['deserializer'](chunk) for chunk in chunks(x,baseTypeCall[base]['size']) ], 
                'serializer':   lambda x: Cstruct.serializeArray(x, intSize, baseTypeCall[base]['serializer'])
                } if base != "char" else {
                'size': intSize*baseTypeCall[base]['size'], 
                'deserializer': lambda x: ''.join([( baseTypeCall[base]['deserializer'](chunk) ).decode("ascii") for chunk in chunks(x,baseTypeCall[base]['size']) ]), 
                'serializer':   lambda x: Cstruct.serializeString(x, intSize)
                }
                
    @staticmethod
    def serializeArray(values, count, serializer):
        if len(values) != count:
            raise ValueError("Array length does not match declared field size")
        return b''.join(map(serializer, values))

    @staticmethod
    def serializeString(value, count):
        encoded = value.encode('ascii')
        if len(encoded) > count:
            raise ValueError("String exceeds declared field size")
        return encoded.ljust(count, b'\x00')

    def __init__(self, fields):
       self.struct = OrderedDict()
       self.initialized = True
       for name in fields:
            if fields[name] in Cstruct.CTypes:
                self.struct[name]=Cstruct.CTypes[fields[name]]
            elif Cstruct.isArrayType(fields[name]):
                self.struct[name]=Cstruct.arrayType(fields[name])
            else:
                raise ValueError("%s Type is not C Struct class compatible."%fields[name])
            
    def __len__(self):
        return sum([self.struct[element]['size'] for element in self.struct])
        
    def marshall(self, data):
        return {varName:typeOperator['deserializer'](data.read(typeOperator['size'])) for varName, typeOperator in self.struct.items()}
    
    def testSerialize(self,varName,data,operator):
        try:
            return operator(data[varName])
        except:
            print("Variable %s was passed %s"%(varName,data[varName]))
            raise
            
    def serialize(self, data):        
        return b''.join((self.testSerialize(varName,data,typeOperator['serializer']) for varName, typeOperator in self.struct.items()))
    
class Mod3Container():
    def __init__(self, Mod3Class, containeeCount = 0):
        self.mod3Array = [Mod3Class() for _ in range(containeeCount)]
    
    def marshall(self, data):
        [x.marshall(data) for x in self.mod3Array]
        
    def construct(self, data):
        if len(data) != len(self.mod3Array):
            raise AssertionError("Cannot construct container with different amounts of data")
        [x.construct(d) for x,d in zip(self.mod3Array,data)]
        
    def serialize(self):
        return b''.join([element.serialize() for element in self.mod3Array])
    
    def __iter__(self):
        return self.mod3Array.__iter__()
    
    def __getitem__(self, ix):
        return self.mod3Array.__getitem__(ix)
    
    def __len__(self):
        if self.mod3Array:
            return len(self.mod3Array)*len(self.mod3Array[0])
        return 0
    
    def append(self, ele):
        self.mod3Array.append(ele)
    
    def pop(self,ix):
        self.mod3Array.pop(ix)
        
    def Count(self):
        return len(self.mod3Array)
    
    def verify(self):
        [x.verify() for x in self.mod3Array]
        
    def __repr__(self):
        return str(list(map(lambda x: repr(x), self.mod3Array)))