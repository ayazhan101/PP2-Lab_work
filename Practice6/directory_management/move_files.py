import shutil
import os

os.makedirs("backup", exist_ok=True)
shutil.move("example.txt", "backup/example.txt")
print("Файл перемещен в папку backup.")