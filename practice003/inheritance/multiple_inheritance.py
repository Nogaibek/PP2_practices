class camera:
    def take_photo(self):
        print("Snap! Photo taken.")

class phone:
    def make_call(self):
        print("Dialing number...")

class smartphone(camera, phone):
    def browse_internet(self):
        print("Opening browser...")

my_phone = smartphone()

my_phone.take_photo()
my_phone.browse_internet()
my_phone.make_call()