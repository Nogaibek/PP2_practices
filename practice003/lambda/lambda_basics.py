add = lambda a, b: a+b
print(add(3, 7))

my_pow = lambda n, p: pow(n, p) 
print(my_pow(10, 2))

def myfunc(n):
  return lambda a : a * n
mytripler = myfunc(3)
print(mytripler(11))

