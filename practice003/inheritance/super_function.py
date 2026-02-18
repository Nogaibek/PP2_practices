class animal:
     def __init__(self, type):
          self.type = type

class dog(animal):
     def __init__(self, name):
          super().__init__("dog")
          self.name = name

my_dog = dog("rocky")
print(my_dog.type, my_dog.name)

