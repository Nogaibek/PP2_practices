class animal:
     def __init__(self, type):
          self.type = type

class my_animal(animal):
     pass 

my_dog = my_animal("rocky")
print(my_dog.type)

