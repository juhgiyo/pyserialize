# pyserialize
Python simple serializer

pyserialize
============

`pyserialize` is a simple python serialization/deserialization library. 

Installation
------------

You can to use [pip](https://pypi.python.org/pypi/pip) to install pyserialize:
``` bash
$ pip install pyserialize
```
Or using last source:
``` bash
$ pip install git+git://github.com/juhgiyo/pyserialize.git
```

Usage Guide
-----------

Supported Format

None, bool, integer, float, string, list, tuple, set, dict, class(subclass of Packable)

For all type except class type, you can simply pack:


```python
from pyserialize import *

...

# Serializing

a=0
b='Hello World'
c=0.05

serializedData=Serializer.pack(a,b,c)

d=[10,20,30]

serializedData2=Serializer.pack(a,b,c,d)

e=(10.0,30.5)
f=None

serializedData2=serializedData2+Serializer.pack(e, f)


# Deserializing

unserializedData=Serializer.unpack(serializedData)

print unserializedData[0] # 0
print unserializedData[1] # 'Hellow World'
print unserializedData[2] # 0.05

unserializedData2=Serializer.unpack(serializedData2)

print unserializedData2[0] # 0
print unserializedData2[1] # 'Hellow World'
print unserializedData2[2] # 0.05
print unserializedData2[3] # [10,20,30]
print unserializedData2[4] # (10.0,30.5)
print unserializedData2[5] # None
```

For class type, the class must be a subclass of Packable and must implement below two functions:


```python
def pack(self):
def unpack(self, data):
```

Also the class's constructor must not require any explicit arguments:

```python
from pyserialize import *

class TempClass(Packable):
    def __init__(self):
        ...

# OR

class TempClass(Packable):
    # This is also fine since all arguments have default values
    def __init__(self,a=0,b=3,c='Hello'):
        ...
```

Sample class declaration for pyserialize:


```python
class Vector3D(Packable):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = lat
        self.y = lon
        self.z = alt

    def pack(self):
        return Serializer.pack(self.x, self.y, self.z)

    # unpack is little tricky.
    # When unpacking the data, "Serialize._unpack" must be used
    # and the function also must return tuple of self and size returned from "Serialize._unpack"
    # to operate correctly
    def unpack(self, data):
        (retTuple , size) = = Serializer._unpack(data)
        count = len(retTuple) # number of entities in the tuple
        self.x = retTuple[0]
        self.y = retTuple[1]
        self.z = retTuple[2]

        # Simple can be done by single line as below :
        # ((self.x, self.y, self.z), size) = Serializer._unpack(data)
        
        return (self, size)

    # Optinal
    def __str__(self):
        return "Vector3D:x=%s,y=%s,z=%s" % (self.x, self.y, self.z)
...

# Now the class can be used as any other supported type for pyserilize
a=0
b='Hello World'
c=0.05
d= Vector3D(5.0,10.0,2.0)

serializedData=Serializer.pack(a,b,c,d)


unserializedData=Serializer.unpack(serializedData)

print unserializedData[0] # 0
print unserializedData[1] # 'Hellow World'
print unserializedData[2] # 0.05
print unserializedData[3] # "Vector3D:x=5.0,y=10.0,z=2.0"
```


Feature Requests and Bug Reports
--------------------------------

Should all be reported on the Github Issue Tracker


Copyright
---------

Copyright (c) 2016 Woong Gyu La <juhgiyo@gmail.com>. See LICENSE for details.