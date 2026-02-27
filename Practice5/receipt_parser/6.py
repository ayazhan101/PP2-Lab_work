import re

text = "Hello, world. Python is fun"

result = re.sub(r"[ ,\.]", ":", text)

print(result)