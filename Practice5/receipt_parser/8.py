import re

text = "HelloWorldPython"

result = re.findall(r"[A-Z][a-z]*", text)

print(result)