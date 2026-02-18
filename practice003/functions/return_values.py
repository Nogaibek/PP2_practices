def is_prime(a):
     for i in range(2, a):
          if a%i == 0:
               print(i)
               return "NO"
     return "YES"
answer = is_prime(13)
print(answer)


def create_list(n):
     return list((i for i in range(n)))
myList = create_list(5)
print(myList)

