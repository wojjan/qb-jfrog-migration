import os
import zipfile
import logging
import sys
import argparse

# ---------------------------------------------
# Logging setup
# ---------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("compare_folders.log", mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# ---------------------------------------------
# Argument parsing
# ---------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Compare two folders including files inside ZIP archives.")
    parser.add_argument('--folder_a', type=str, help='Path to folder A')
    parser.add_argument('--folder_b', type=str, help='Path to folder B')
    parser.add_argument('--folders_file', type=str, help='File with two lines: pathA, pathB')
    return parser.parse_args()


# ---------------------------------------------
# Reading A/B folders from text file
# ---------------------------------------------
def get_folders_from_file(file_path):
    abs_path = os.path.abspath(file_path)

    if not os.path.exists(abs_path):
        logging.error(f"Input file not found: {abs_path}")
        print(f"ERROR: Input file not found: {abs_path}")
        sys.exit(1)

    with open(abs_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) < 2:
        logging.error(f"{abs_path} must contain at least two lines")
        print(f"ERROR: {abs_path} must contain at least two lines")
        sys.exit(1)

    logging.info(f"Folder A = {lines[0]}")
    logging.info(f"Folder B = {lines[1]}")

    return lines[0], lines[1]


# ---------------------------------------------
# Check if a file path exists inside a zip
# ---------------------------------------------
def file_in_zip(zip_path, inner_path):
    inner_zip_style = inner_path.replace(os.sep, "/")

    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            return inner_zip_style in z.namelist()
    except Exception as e:
        logging.error(f"Error reading ZIP: {zip_path}: {e}")
        return False


# ---------------------------------------------
# List all files (including zip-internal) recursively
# ---------------------------------------------
def list_files_in_folder(folder):
    files = []
    for root, _, filenames in os.walk(folder):
        #logging.info(f"Walking: {root}")
        for filename in filenames:
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, folder)
            files.append(rel_path)
    return files


# ---------------------------------------------
# Noramlize path
# ---------------------------------------------
def normalize_path(path, find_string, replace_string):
    """
    Replace find_string with replace_string only inside file/folder names,
    not touching directory separators.
    """
    base = os.path.basename(path)
    dirpath = os.path.dirname(path)

    # Only swap in basename
    if find_string in base:
        base = base.replace(find_string, replace_string)

    return os.path.join(dirpath, base).replace("\\", "/")


# ---------------------------------------------
# Compare A → B
# ---------------------------------------------
def compare_folders_inside_zip_files_too(folder_a, folder_b):
    counters = {'processed': 0, 'found': 0, 'unpacked': 0, 'missing': 0}
    missing = []

    # Output files
    present_file = open("present.txt", "w", encoding="utf-8")
    present_zip_file = open("present_in_zip.txt", "w", encoding="utf-8")
    missing_file = open("missing.txt", "w", encoding="utf-8")

    files_a = list_files_in_folder(folder_a, counters)

    for rel in files_a:
        counters['processed'] += 1

        target_full = os.path.join(folder_b, rel)

        # -------------------------------------------
        # CASE 1 — file exists directly in folder_b
        # -------------------------------------------
        if os.path.exists(target_full):
            logging.info(f"Present: {rel}")
            counters['found'] += 1
            present_file.write(rel + "\n")
            continue

        # -------------------------------------------
        # CASE 2 — maybe inside ZIP
        # -------------------------------------------
        parts = rel.split(os.sep)
        found = False

        for i in range(len(parts)):
            if parts[i].lower().endswith('.zip'):
                zip_path = os.path.join(folder_b, *parts[:i+1])
                remaining = parts[i+1:]

                if not remaining:
                    continue

                inner_file = os.path.join(*remaining)

                if os.path.exists(zip_path) and file_in_zip(zip_path, inner_file):

                    logging.info(
                        "Present inside ZIP:\n"
                        f"  File: {rel}\n"
                        f"  ZIP : {zip_path}"
                    )

                    counters['found'] += 1

                    # write to both "present" and "present_in_zip"
                    present_file.write(f"{rel}  [ZIP: {zip_path}]\n")
                    present_zip_file.write(f"{rel}  [ZIP: {zip_path}]\n")

                    found = True
                    break

        # -------------------------------------------
        # CASE 3 — missing file
        # -------------------------------------------
        if not found:
            logging.warning(f"Missing: {rel}")
            counters['missing'] += 1
            missing.append(rel)
            missing_file.write(rel + "\n")

    # Close files
    present_file.close()
    present_zip_file.close()
    missing_file.close()

    return missing, counters


def compare_folders(folder_a, folder_b):
    files_a = set(list_files_in_folder(folder_a))
    #logging.info(f"files_a = {files_a}")
    files_b = set(list_files_in_folder(folder_b))
    #logging.info(f"files_b = {files_b}")

    missing = files_a - files_b
    extra = files_b - files_a
    present = files_a & files_b

    # Output results
    with open("missing.txt", "w", encoding="utf-8") as f:
        for rel in sorted(missing):
            f.write(rel + "\n")
    with open("extra.txt", "w", encoding="utf-8") as f:
        for rel in sorted(extra):
            f.write(rel + "\n")
    with open("present.txt", "w", encoding="utf-8") as f:
        for rel in sorted(present):
            f.write(rel + "\n")
            logging.info(f"Present: {rel}")

    return missing, extra, present



# ---------------------------------------------
# MAIN
# ---------------------------------------------
if __name__ == "__main__":
    args = parse_args()

    if args.folders_file:
        A, B = get_folders_from_file(args.folders_file)
    elif args.folder_a and args.folder_b:
        A, B = args.folder_a, args.folder_b
    else:
        print("You must specify either --folders_file or both --folder_a and --folder_b")
        sys.exit(1)

    # --- Add verification for folder existence ---
    if not os.path.exists(A):
        logging.error(f"Folder A does not exist: {A}")
        print(f"ERROR: Folder A does not exist: {A}")
        sys.exit(1)
    if not os.path.exists(B):
        logging.error(f"Folder B does not exist: {B}")
        print(f"ERROR: Folder B does not exist: {B}")
        sys.exit(1)

    missing_files, extra_files, present_files = compare_folders(A, B)

    if missing_files:
        logging.warning("==== Missing files ====")
        for f in missing_files:
            logging.warning("  " + f)
    else:
        logging.info("All files from A exist in B!")

    logging.info("==== Summary Report of comparison A and B ====")
    logging.info(f"A = {A}")
    logging.info(f"B = {B}")
    logging.info(f"Total files in A: {len(set(list_files_in_folder(A)))}")
    logging.info(f"Total files in B: {len(set(list_files_in_folder(B)))}")
    logging.info(f"Files missing in B: {len(missing_files)}")
    logging.info(f"Extra files in B: {len(extra_files)}")
    logging.info(f"Files present in both: {len(present_files)}")
