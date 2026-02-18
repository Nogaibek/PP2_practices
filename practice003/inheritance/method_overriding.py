class animal:
    def speak(self):
        print("The animal makes a generic sound.")

class dog(animal):
    def speak(self):
        print("The dog barks: Woof! Woof!")

other_animal = animal()
myDog = dog()

myDog.speak()
other_animal.speak()