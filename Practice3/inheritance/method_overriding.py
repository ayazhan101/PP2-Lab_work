class Animal:
    def speak(self):
        print("Animal makes a sound")


class Cat(Animal):
    def speak(self):
        print("Cat meows") 

animal = Animal()
cat = Cat()

animal.speak()
cat.speak()
