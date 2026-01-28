

#data types in python

#int
x = 5
y = 10
z = x + y
print(type(x))
print(type(y))
print(type(z))


#complex
c = 3 + 4j
y = 5 + 2j
z = c + y
print(type(c))
print(type(y))
print(type(z))


#range
r = range(6)
y = range(1, 10)
z = range(2, 20, 3)
print(type(r))


#frozenset
fset = frozenset([1, 2, 3, 4])
y = frozenset(("apple", "banana", "cherry"))
z = frozenset({5, 6, 7, 8})
print(type(fset))
print(type(y))
print(type(z))


#bytes
b = bytes(5)
y = b"Hello"
z = bytes([65, 66, 67])
print(type(b))
print(type(y))
print(type(z))



#bytearray
barr = bytearray(5)
y = bytearray(b"Hello")
z = bytearray([65, 66, 67])
print(type(barr))
print(type(y))
print(type(z))


#memoryview
mv = memoryview(bytes(5))
y = memoryview(b"Hello")
z = memoryview(bytearray([65, 66, 67]))
print(type(mv))
print(type(y))
print(type(z))


#none type
n = None
print(type(n))


#float
y = 3.14
x = 2.71
z = x + y
print(type(x))
print(type(z))
print(type(y))


#string
name = "John"
color = 'Blue'
animal = """Dog"""
print(type(name))
print(type(color))
print(type(animal))


#bool
is_active = True
is_admin = False
idle = (5 > 10)
print(type(is_active))
print(type(is_admin))
print(type(idle))


#list
fruits = ["Apple", "Banana", "Cherry"]
animals = ['Dog', 'Cat', 'Elephant']
names = [ "Alice", "Bob", "Charlie"]
print(type(fruits))
print(type(animals))
print(type(names))


#tuple
coordinates = (10, 20)
pair = (1, 2)
point = (5, 15)
print(type(coordinates))
print(type(pair))
print(type(point))


#set
unique_numbers = {1, 2, 2, 2, 3, 4, 5, 5, 5, 5}
unique_letters = {'a', 'b', 'b', 'c', 'd', 'd'}
unique_values = {10, 20, 20, 30, 40, 40}
print(type(unique_letters))
print(type(unique_values))
print(type(unique_numbers))


#dictionary
person = {"name": "Alice", "age": 30}
data = {"city": "New York", "country": "USA"}
info = {"brand": "Toyota", "model": "Camry"}
print(type(person))
print(type(data))
print(type(info))


#Output
#<class 'int'>
#<class 'float'>
#<class 'str'>
#<class 'bool'>
#<class 'list'>
#<class 'tuple'>
#<class 'set'>
#<class 'dict'>
#<class 'complex'>
#<class 'range'>
#<class 'frozenset'>
#<class 'bytes'>
#<class 'bytearray'>
#<class 'memoryview'>
#<class 'NoneType'>
