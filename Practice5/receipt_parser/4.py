import re

text = "Hello world Test ABC Apple"

pattern = r"[A-Z][a-z]+"

print(re.findall(pattern, text))