class animal:
    def speak(self):
        print("The animal makes a generic sound.")

class dog(animal):
    def speak(self):
        print("The dog barks: Woof! Woof!")

myDog = dog()
myDog.speak()