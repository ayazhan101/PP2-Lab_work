names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]

for index, name in enumerate(names):
    print(f"{index}: {name}")

for name, age in zip(names, ages):
    print(f"{name} is {age} years old")