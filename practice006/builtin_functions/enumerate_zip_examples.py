animal = ["dog", "cat", "mouse", "hourse", "elephant", "giraffe"]
ages = [8, 3, 5, 4, 3, 5]
for index, name in enumerate(animal):
    print(f"{index + 1}. {name}")
for name, number in zip(animal, ages):
    print(f"{name}, {number} years old")