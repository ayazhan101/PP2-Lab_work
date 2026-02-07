class Student:
    university = "KBTU"   

    def __init__(self, name):
        self.name = name  

s1 = Student("Arman")
s2 = Student("Dana")

print(s1.name, s1.university)
print(s2.name, s2.university)

Student.university = "MIT"

print(s1.university)
print(s2.university)
