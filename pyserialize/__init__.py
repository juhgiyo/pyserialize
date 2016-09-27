#!/usr/bin/python
"""
@file Serializer.py
@author Woong Gyu La a.k.a Chris. <juhgiyo@gmail.com>
        <http://github.com/juhgiyo/pyserialize>
@date March 10, 2016
@brief Serializer Interface
@version 0.1

@section LICENSE

The MIT License (MIT)

Copyright (c) 2016 Woong Gyu La <juhgiyo@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

@section DESCRIPTION

Definitions for Serializer Class.
"""

import importlib
import inspect
from struct import *

'''
format
    None: n
    bool: ?
    int: q
    float: d
    str: s

    list: a
    set: t
    dict: m
    tuple: u
    class: o (class must be a subclass of Packable class)

NOT SUPPORTED:
    x / p / P
'''


def str_to_class(module_name, class_name):
    m = importlib.import_module(module_name)
    c = getattr(m, class_name)
    return c


class Packable(object):
    """
    this function must return the packed data of the class
    """

    def pack(self):
        raise NotImplementedError()

    '''
    data can be longer than it is needed,
    so you must provide way to unpack the data with extra bytes.
    Also this function must return the tuple of object and size, it has used 
    example: return (object,size)
    '''

    def unpack(self, data):
        raise NotImplementedError()


class Serializer(object):
    @staticmethod
    def pack(*arg):
        data = ''
        fmt = pack('= I', len(arg))
        for item in arg:
            if item is None:
                fmt += 'n'
            elif type(item) == bool:
                data += pack('= ?', item)
                fmt += '?'
            elif type(item) == int:
                data += pack('= q', item)
                fmt += 'q'
            elif type(item) == float:
                data += pack('= d', item)
                fmt += 'd'
            elif type(item) == str:
                data += pack('= I %ds' % (len(item),), len(item), item)
                fmt += 's'
            elif type(item) == list:
                fmt += 'a'
                data += Serializer.pack(*item)
            elif type(item) == tuple:
                fmt += 'u'
                data += Serializer.pack(*item)
            elif type(item) == set:
                fmt += 't'
                data += Serializer.pack(*list(item))
            elif type(item) == dict:
                fmt += 'm'
                dict_list = []
                for key, value in item.iteritems():
                    dict_list.append(key)
                    dict_list.append(value)
                data += Serializer.pack(*item)
            elif issubclass(type(item), Packable):
                fmt += 'o'
                data += pack('= I %ds I %ds' % (len(item.__module__), len(item.__class__.__name__)),
                             len(item.__module__), item.__module__, len(item.__class__.__name__),
                             item.__class__.__name__)
                data += item.pack()
            else:
                raise Exception('Unpackable object inserted: %s' % (item,))
        return fmt + data

    @staticmethod
    def unpack(data):
        # ret_list = []
        orig_size = len(data)

        (ret_tuple, used_size) = Serializer._unpack(data)
        ret_list = list(ret_tuple)
        left_size = orig_size - used_size
        should_break = False
        while left_size > 0:
            try:

                (ret_tuple, used_size) = Serializer._unpack(data)

                ret_list = ret_list + list(ret_tuple)
                left_size = left_size - used_size

            except Exception:
                should_break = True
            if should_break:
                break
        return tuple(ret_list)

    @staticmethod
    def _unpack(data):
        used_size = 0
        (format_len,), data = unpack('= I', data[:4]), data[4:]
        used_size += 4
        fmt, data = data[:format_len], data[format_len:]
        used_size += format_len
        ret_list = []

        for i in range(format_len):
            if fmt[i] == 'n':
                ret_list.append(None)
            elif fmt[i] == '?':
                (ret_data,), data = unpack('= ?', data[:1]), data[1:]
                used_size += 1
                ret_list.append(ret_data)

            elif fmt[i] == 'q':
                (ret_data,), data = unpack('= q', data[:8]), data[8:]
                used_size += 8
                ret_list.append(ret_data)

            elif fmt[i] == 'd':
                (ret_data,), data = unpack('= d', data[:8]), data[8:]
                used_size += 8
                ret_list.append(ret_data)

            elif fmt[i] == 's':
                (str_len,), data = unpack('= I', data[:4]), data[4:]
                used_size += 4
                ret_list.append(data[:str_len])
                data = data[str_len:]
                used_size += str_len

            elif fmt[i] == 'a':
                (ret_tuple, size) = Serializer._unpack(data)
                used_size += size
                ret_list.append(list(ret_tuple))

            elif fmt[i] == 'u':
                (ret_tuple, size) = Serializer._unpack(data)
                used_size += size
                ret_list.append(ret_tuple)

            elif fmt[i] == 't':
                (ret_tuple, size) = Serializer._unpack(data)
                used_size += size
                ret_list.append(set(ret_tuple))

            elif fmt[i] == 'm':
                (ret_tuple, size) = Serializer._unpack(data)
                ret_list = list(ret_tuple)
                ret_map = {}
                for j in xrange(0, len(ret_list), 2):
                    ret_map[ret_list[j]] = ret_list[j + 1]
                used_size += size
                ret_list.append(ret_map)

            elif fmt[i] == 'o':
                (module_name_len,), data = unpack('= I', data[:4]), data[4:]
                used_size += 4
                module_name, data = data[:module_name_len], data[module_name_len:]
                used_size += module_name_len
                (class_name_len,), data = unpack('= I', data[:4]), data[4:]
                used_size += 4
                class_name, data = data[:class_name_len], data[class_name_len:]
                used_size += class_name_len

                m = importlib.import_module(module_name)
                c = getattr(m, class_name)

                info = inspect.getargspec(c.__init__)
                args = ()
                for j in range(len(info.args) - 1 - len(info.defaults)):
                    args += (None,)

                (ret_object, size) = c(*args).unpack(data)
                data = data[size:]
                used_size += size
                ret_list.append(ret_object)

            elif fmt[i] == 'c':
                (ret_data,), data = unpack('= c', data[:1]), data[1:]
                used_size += 1
                ret_list.append(ret_data)
            elif fmt[i] == 'b':
                (ret_data,), data = unpack('= b', data[:1]), data[1:]
                used_size += 1
                ret_list.append(ret_data)
            elif fmt[i] == 'B':
                (ret_data,), data = unpack('= B', data[:1]), data[1:]
                used_size += 1
                ret_list.append(ret_data)
            elif fmt[i] == 'h':
                (ret_data,), data = unpack('= h', data[:2]), data[2:]
                used_size += 2
                ret_list.append(ret_data)
            elif fmt[i] == 'H':
                (ret_data,), data = unpack('= H', data[:2]), data[2:]
                used_size += 2
                ret_list.append(ret_data)
            elif fmt[i] == 'i':
                (ret_data,), data = unpack('= i', data[:4]), data[4:]
                used_size += 4
                ret_list.append(ret_data)
            elif fmt[i] == 'I':
                (ret_data,), data = unpack('= I', data[:4]), data[4:]
                used_size += 4
                ret_list.append(ret_data)
            elif fmt[i] == 'l':
                (ret_data,), data = unpack('= l', data[:4]), data[4:]
                used_size += 4
                ret_list.append(ret_data)
            elif fmt[i] == 'L':
                (ret_data,), data = unpack('= L', data[:4]), data[4:]
                used_size += 4
                ret_list.append(ret_data)
            elif fmt[i] == 'Q':
                (ret_data,), data = unpack('= Q', data[:8]), data[8:]
                used_size += 8
                ret_list.append(ret_data)
            elif fmt[i] == 'f':
                (ret_data,), data = unpack('= f', data[:4]), data[4:]
                used_size += 4
                ret_list.append(ret_data)
            elif fmt[i] == 'x':
                raise Exception("x is not a supported format")
            elif fmt[i] == 'p':
                raise Exception("p is not a supported format")
            elif fmt[i] == 'P':
                raise Exception("P is not a supported format")
        return tuple(ret_list), used_size
