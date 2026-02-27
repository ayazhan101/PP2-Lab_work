import re

text = "hello_world test_example Wrong_Test"

pattern = r"[a-z]+_[a-z]+"

print(re.findall(pattern, text))