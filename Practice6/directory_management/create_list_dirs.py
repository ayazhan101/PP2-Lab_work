import os

os.makedirs("new_folder", exist_ok=True)
print("Директория создана.")
dirs = [d for d in os.listdir() if os.path.isdir(d)]
print("Список директорий:", dirs)