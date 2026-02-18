def my_pow(a, b):
     x = 1
     while(b != 0):
          x *= a
          b -= 1
     print(x)

my_pow(2, 3)


def convert(f, c, num):
     if f.lower() == 'c' and c.lower() == 'f':
          print(((num*9)/5)+32)
     elif f.lower() == 'f' and c.lower() == 'c':
          print(((num-32)*5)/9)
     else:
          print("error")
     
convert('f', 'c', 2)

