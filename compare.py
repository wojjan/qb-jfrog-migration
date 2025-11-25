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
def list_files_in_folder(folder, counters):
    files = []

    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, folder)

            if filename.lower().endswith('.zip'):
                try:
                    with zipfile.ZipFile(full_path, 'r') as z:
                        for zipinfo in z.infolist():
                            if not zipinfo.is_dir():
                                entry = os.path.join(rel_path, zipinfo.filename)
                                files.append(entry)
                                counters['unpacked'] += 1
                                logging.info(f"ZIP: {rel_path} -> {zipinfo.filename}")
                except Exception as e:
                    logging.error(f"Cannot read ZIP: {full_path}: {e}")
            else:
                files.append(rel_path)

    return files


# ---------------------------------------------
# Compare A → B
# ---------------------------------------------
def compare_folders(folder_a, folder_b):
    counters = {'processed': 0, 'found': 0, 'unpacked': 0, 'missing': 0}
    missing = []

    files_a = list_files_in_folder(folder_a, counters)

    for rel in files_a:
        counters['processed'] += 1

        # direct path
        target_full = os.path.join(folder_b, rel)

        if os.path.exists(target_full):
            logging.info(f"Present: {rel}")
            counters['found'] += 1
            continue

        # maybe inside a ZIP
        parts = rel.split(os.sep)
        found = False

        for i in range(len(parts)):
            if parts[i].lower().endswith('.zip'):
                zip_path = os.path.join(folder_b, *parts[:i+1])

                remaining = parts[i+1:]

                # If there is no inner file (e.g. "file.zip"), skip
                if len(remaining) == 0:
                    continue

                inner_file = os.path.join(*remaining)

                if os.path.exists(zip_path) and file_in_zip(zip_path, inner_file):
                    #logging.info(f"Present inside ZIP: {rel}  (ZIP: {zip_path})")
                    logging.info(
                        "Present inside ZIP:\n"
                        f"  File: {rel}\n"
                        f"  ZIP : {zip_path}"
                    )


                    counters['found'] += 1
                    found = True
                    break

        if not found:
            logging.warning(f"Missing: {rel}")
            counters['missing'] += 1
            missing.append(rel)

    return missing, counters


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

    missing_files, counters = compare_folders(A, B)

    if missing_files:
        logging.warning("==== Missing files ====")
        for f in missing_files:
            logging.warning("  " + f)
    else:
        logging.info("All files from A exist in B!")

    logging.info("==== Summary Report of comarison A and B ====")
    logging.info(f"A = {A}")
    logging.info(f"B = {B}")
    logging.info(f"Total processed: {counters['processed']}")
    logging.info(f"Files unpacked from zips: {counters['unpacked']}")
    logging.info(f"Files found: {counters['found']}")
    logging.info(f"Files missing: {counters['missing']}")
