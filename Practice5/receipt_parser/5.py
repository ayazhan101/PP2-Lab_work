import re

pattern = r"a.*b"

strings = ["ab", "axxb", "a123b", "ac"]

for s in strings:
    if re.fullmatch(pattern, s):
        print(s, "-> Match")