

#type of variables
x = 5               #int
y = 3.14            #float
name = "John"      #string
is_student = True   #boolean
#Output
print(x)
print(y)
print(name)
print(is_student)


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


#Multiple assignments
a, b, c = 1, 2.5, "Hello"
d = map(int, input("Enter three numbers separated by spaces: ").split())
#Output multiple assignments
print(a)
print(b)
print(c)
print(list(d))

#Constants (by convention, using uppercase variable names)
PI = 3.14159
GRAVITY = 9.81
#Output constants
print("Value of PI:", PI)
print("Value of GRAVITY:", GRAVITY)


#get the type of variable
print(type(x))
print(type(y))
print(type(name))
print(type(is_student))
print(type(age))
print(type(height))
print(type(num_int))
print(type(num_float))
print(type(PI))
print(type(GRAVITY))
