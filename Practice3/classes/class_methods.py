class Person:
    def __init__(self, name):
        self.name = name

    def say_hello(self):
        print(f"Hello, my name is {self.name}")

    def change_name(self, new_name):
        self.name = new_name

p = Person("Arman")
p.say_hello()

p.change_name("John")
p.say_hello()
