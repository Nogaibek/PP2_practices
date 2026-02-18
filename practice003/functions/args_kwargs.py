def hello(*names):
     for name in names:
          print('Hello,', name)
hello('didar', 'piwi', 'fred')

def which_car(**id_cars):
     print(cars[id_cars["first"]])
     print(cars[id_cars["second"]])
     print(cars[id_cars["third"]])

cars = ['a', 'b', 's']
which_car(first = 0, second = 1, third = 2)