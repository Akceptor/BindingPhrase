import hashlib
import itertools
import string
import concurrent.futures
import multiprocessing
import time
import os
from datetime import datetime

# Get current time as a formatted string
def current_time():
    return datetime.now().strftime("%H:%M:%S")

# Compute first 6 bytes of an MD5 hash
def get_uid_bytes(value):
    return list(hashlib.md5(value.encode()).digest()[0:6])

# Get the directory of the script
script_directory = os.path.dirname(os.path.abspath(__file__))

# File path relative to the script's directory
file_path = os.path.join(script_directory, "md5_list.txt")

# Load precomputed hashes into memory
def load_precomputed_md5(file_path="md5_list.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            # Process each line: The part before ":" is the UID, and the part after is the word
            return {tuple(map(int, line.split(":")[1].split(","))): line.split(":")[0].strip() for line in file if ':' in line}
    except FileNotFoundError:
        print(f"[{current_time()}] ⚠ Precomputed MD5 file '{file_path}' not found.")
        return {}

# Try to find the UID in the precomputed hash list
def check_precomputed_md5(target_uid, precomputed_hashes):
    return precomputed_hashes.get(tuple(target_uid))

# Brute-force function with multiprocessing (if no precomputed match)
def brute_force_search(target_uid):
    charset = string.ascii_letters + string.digits + string.punctuation
    max_length = 6
    num_workers = multiprocessing.cpu_count()

    print(f"[{current_time()}] Using {num_workers} CPU cores for brute-force.")
    print(f"[{current_time()}] Searching... This may take time.")

    start_time = time.time()

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        for length in range(1, max_length + 1):
            candidates = (''.join(p) for p in itertools.product(charset, repeat=length))
            batch_size = 500000

            while True:
                batch = list(itertools.islice(candidates, batch_size))
                if not batch:
                    break

                future = executor.submit(check_batch, batch, target_uid)
                result = future.result()

                if result:
                    end_time = time.time()
                    print(f"[{current_time()}] ✅ Match found: {result}")
                    print(f"[{current_time()}] ⏱ Time taken: {end_time - start_time:.2f} seconds")
                    return

    end_time = time.time()
    print(f"[{current_time()}] ❌ No match found.")
    print(f"[{current_time()}] ⏱ Time taken: {end_time - start_time:.2f} seconds")

# Generate and check a batch of candidates
def check_batch(batch, target_uid):
    for test_string in batch:
        if get_uid_bytes(test_string) == target_uid:
            return test_string
    return None

# Convert user input into a list of integers
def get_target_uid():
    while True:
        try:
            user_input = input(f"\n[{current_time()}] Enter target UID array (comma-separated numbers, e.g., 9,143,107,205,70,33): ")
            uid_list = [int(x.strip()) for x in user_input.split(",")]
            if len(uid_list) == 6 and all(0 <= x <= 255 for x in uid_list):
                return uid_list
            else:
                print(f"[{current_time()}] ⚠ Invalid input. Enter exactly 6 numbers (0-255) separated by commas.")
        except ValueError:
            print(f"[{current_time()}] ⚠ Invalid input. Please enter numbers only.")

# Main menu
def main():
    precomputed_hashes = load_precomputed_md5(file_path)  # Load precomputed hashes once

    while True:
        print(f"\n[{current_time()}] Choose an option:")
        print(f"[{current_time()}] 1. Convert text to UID array")
        print(f"[{current_time()}] 2. Find text from UID array (precomputed MD5 + brute-force)")
        print(f"[{current_time()}] 3. Exit")

        choice = input(f"[{current_time()}] Enter your choice (1/2/3): ").strip()

        if choice == "1":
            text = input(f"\n[{current_time()}] Enter the text: ").strip()
            modified_word = f'-DMY_BINDING_PHRASE="{text}"'
            uid_array = get_uid_bytes(modified_word)
            print(f"[{current_time()}] 🆔 UID array: {uid_array}")

        elif choice == "2":
            target_uid = get_target_uid()

            # Try precomputed hashes first
            print(f"[{current_time()}] 🔍 Checking precomputed hashes...")
            match = check_precomputed_md5(target_uid, precomputed_hashes)
            if match:
                print(f"[{current_time()}] ✅ Found in precomputed MD5 list: {match}")
                return

            # If not found, brute-force
            brute_force_search(target_uid)

        elif choice == "3":
            print(f"[{current_time()}] 👋 Exiting...")
            break

        else:
            print(f"[{current_time()}] ⚠ Invalid choice. Please enter 1, 2, or 3.")

# Run the program
if __name__ == "__main__":
    main()
