class person:
     def __init__(self, name, age, university):
          self.name = name
          self.age = age
          self.university = university
          self.skills = []

     def who(self):
          print("He is", self.name)
     
     def how_old(self):
          print(self.age, 'years old')
     
     def study(self):
          print(self.university)

     def add_skills(self, skill):
          self.skills.append(skill)
          print(f"{skill} added")
     

human = person('Danial', 18, 'KBTU')

human.who()
human.how_old()
human.study()
human.add_skills('c++')
