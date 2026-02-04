n = 10
while n > 0:
     n -= 1
     if n % 2 == 0:
          continue
     print(n)

names = ['Alice', 'Bob', 'Charlie', 'David']
index = 0
while index < len(names):
     name = names[index]
     index += 1
     if name[0] != 'C':
          continue
     print(name)

