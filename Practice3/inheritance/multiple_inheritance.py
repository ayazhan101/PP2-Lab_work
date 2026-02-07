class Flyable:
    def fly(self):
        print("I can fly")


class Swimmable:
    def swim(self):
        print("I can swim")


class Duck(Flyable, Swimmable):
    def sound(self):
        print("Duck quacks")


duck = Duck()
duck.fly()
duck.swim()
duck.sound()
