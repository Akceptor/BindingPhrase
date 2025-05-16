import hashlib
import os

script_directory = os.path.dirname(os.path.abspath(__file__))

bindphrases_path = os.path.join(script_directory, "bindphrases.txt")

output_path = os.path.join(script_directory, "md5_list.txt")

with open(bindphrases_path, "r") as f:
    words = [line.strip() for line in f if line.strip()]  

with open(output_path, "w") as file:
    for word in words:
        modified_word = f'-DMY_BINDING_PHRASE="{word}"'
        uid_bytes = hashlib.md5(modified_word.encode()).digest()[0:6]
        hex_uid = ",".join(str(b) for b in uid_bytes)
        file.write(f"{word}:{hex_uid}\n")

print(f"Precomputed MD5 hashes saved to {output_path}")
