class person:
     def __init__(self, name, age, university):
          self.name = name
          self.age = age
          self.university = university
          self.skills = []
     
human = person('Danial', 18, 'KBTU')
print(human.name)
print(human.age)
print(human.university)
