import re

pattern = r"ab*"

strings = ["a", "ab", "abb", "ac"]

for s in strings:
    if re.fullmatch(pattern, s):
        print(s, "-> Match")