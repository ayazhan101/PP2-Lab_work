from datetime import datetime

format_str = "%Y-%m-%d %H:%M:%S"

d1 = datetime.strptime(input(), format_str)
d2 = datetime.strptime(input(), format_str)

print(int((d2 - d1).total_seconds()))