import os
import sys
import random
import string

def generate_text_files(root_dir, num_files):
    os.makedirs(root_dir, exist_ok=True)
    for i in range(num_files):
        lines = []
        for _ in range(random.randint(5, 20)):
            word = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 10)))
            lines.append(word)
        if random.random() < 0.3:
            lines.append("special_keyword")
        content = ' '.join(lines)
        filename = os.path.join(root_dir, f"file_{i}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"Generated {num_files} text files in {root_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_text_files.py <folder> <number_of_files>")
        sys.exit(1)
    generate_text_files(sys.argv[1], int(sys.argv[2]))