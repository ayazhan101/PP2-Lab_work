import re

pattern = r"ab{2,3}"

strings = ["abb", "abbb", "ab", "abbbb"]

for s in strings:
    if re.fullmatch(pattern, s):
        print(s, "-> Match")