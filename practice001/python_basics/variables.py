

#Creating Variables
x = 5               #int
y = 3.14            #float
name = "harry"       #string
x = "mart"
X = 45        #x is now of type str
#Output
print(x)
print(X)
print(y)
print(name)


#casting variables
num_str = "100"
num_int = int(num_str)      #casting string to int
num_float = float(num_str)  #casting string to float
#Output after casting
print(num_int)
print(num_float)


#Taking input from user
age = int(input("Enter your age: "))
height = float(input("Enter your height in meters: "))
#Output user input
print("Your age is:", age)
print("Your height is:", height)


#Camel Case
myColor = "red"
#Pascal Case
MyColor = "red"
#Snake Case
My_color = "red"


#Many Values to Multiple Variables
x, y, z = "c++", "python", "java"
c, d, e = 1, 2.5, "hello"
f, g, h = True, False, None
j, k, l = [1,2], (3,4), {5,6}
n, o, p = {"a":1}, b"byte", bytearray(5)
print(x)
print(y)
print(z)
print(c)
print(d)
print(e)
print(f)
print(g)
print(h)
print(j)
print(k)
print(l)
print(n)
print(o)
print(p)


#One Value to Multiple Variables
x = y = z = "Orange"
c = d = e = 10
f = g = h = 3.14
j = k = l = False
n = o = p = [7,8,9]
print(x)
print(y)
print(z)
print(c)
print(d)
print(e)
print(f)
print(g)
print(h)
print(j)
print(k)
print(l)
print(n)
print(o)
print(p)


#Unpack a Collection
language = ["c++", "python", "java"]
x, y, z = language
print(x)
print(y)
print(z)


#Output Variables
x = "good"
print("java is " + x)
y = "great"
print("java is " + y)
a = 5
b = 10
print(a + b)


#Global Variables
x = "good"
def myfunc():
  print("java is " + x)
myfunc()
def myfunc2():
  x = "fantastic"
  print("java is " + x)
myfunc2()
