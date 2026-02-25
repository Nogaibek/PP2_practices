import math as m


#1
n = int(input("Input degree: "))
print(f"Output radian: {(n*m.pi)/180}")

#2
a = int(input("Height: "))
b = int(input("Base, first value: "))
c = int(input("Base, second value: "))
print(f"Expected Output: {((b + c) * a) / 2}")  

#3
a = int(input("Input number of sides: "))
b = int(input("Input the length of a side: "))
print(f"The area of the polygon is: {(a * (b ** 2)) // (4 * m.tan(m.pi / a))}")

#4
a = int(input("Length of base: "))
b = int(input("Height of parallelogram: "))
print(f"Area of the parallelogram: {float(a * b)}")