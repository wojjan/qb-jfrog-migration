import os
import sys
import logging
import zipfile
import argparse
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

print("CWD =", os.getcwd())

# =====================================================
# LOGGING SETUP
# =====================================================
root = logging.getLogger()

for h in root.handlers[:]:
    root.removeHandler(h)
root.setLevel(logging.DEBUG)

# --- Full log ---
full_handler = logging.FileHandler("compare_folders.log", mode="w", encoding="utf-8")
full_handler.setLevel(logging.INFO)
full_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

# --- Summary log ---
summary_handler = logging.FileHandler("summary.log", mode="w", encoding="utf-8")
summary_handler.setLevel(logging.INFO)
summary_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

# --- Console ---
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(message)s"))

root.addHandler(full_handler)
root.addHandler(summary_handler)
root.addHandler(console_handler)

# --- Diagnostic logger ---
diag_handler = logging.FileHandler("diagnostic.log", mode="w", encoding="utf-8")
diag_handler.setLevel(logging.INFO)
diag_handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
diag = logging.getLogger("diag")
diag.setLevel(logging.INFO)
diag.addHandler(diag_handler)

# =====================================================
# ARGUMENTS
# =====================================================
def parse_args():
    parser = argparse.ArgumentParser(
        description="Compare two folders with version replacement and ZIP support."
    )

    parser.add_argument('--folder_a', type=str, help='Path to folder A')
    parser.add_argument('--folder_b', type=str, help='Path to folder B')
    parser.add_argument('--folders_file', type=str, help='File with two lines: pathA, pathB')

    parser.add_argument(
        "--zip-search",
        action="store_true",
        help="Enable searching for files inside ZIP archives (default: disabled)"
    )

    return parser.parse_args()

def get_folders_from_file(file_path):
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        logging.error(f"Input file not found: {abs_path}")
        sys.exit(1)

    with open(abs_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) < 2:
        logging.error(f"{abs_path} must contain at least two non-empty lines")
        sys.exit(1)

    logging.info(f"Folder A = {lines[0]}")
    logging.info(f"Folder B = {lines[1]}")
    return lines[0], lines[1]

# =====================================================
# BUILD EXTRACTION
# =====================================================
def extract_build(name: str):
    """Wyciąga pełną wersję typu 06.03.04.080.0"""
    m = re.search(r"(\d+\.\d+\.\d+\.\d+\.\d+)$", name)
    return m.group(1) if m else None

# =====================================================
# FILE LISTING
# =====================================================
def list_files_in_folder(folder):
    return [os.path.relpath(os.path.join(dp, f), folder)
            for dp, dn, filenames in os.walk(folder) for f in filenames]

# =====================================================
# PATH NORMALIZATION & REPLACEMENT
# =====================================================
def normalize_path_for_compare(rel_path, find_s, replace_s):
    """Replace all occurrences and normalize slashes."""
    if not find_s:
        return rel_path.replace("\\", "/")
    return rel_path.replace(find_s, replace_s).replace("\\", "/")

# =====================================================
# ZIP CHECK
# =====================================================
def file_in_zip(zip_path, inner_path):
    inner_norm = inner_path.replace("\\", "/")
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            found = any(name.endswith(inner_norm) for name in z.namelist())
            diag.info(f"Checking ZIP: {zip_path}, inner={inner_norm}, found={found}")
            return found
    except Exception as e:
        diag.info(f"Error reading ZIP {zip_path}: {e}")
        return False

# =====================================================
# HELPER: find file in B
# =====================================================
def find_file_in_B(mapped_rel, folder_B):
    candidate = os.path.join(folder_B, mapped_rel)
    if os.path.exists(candidate):
        return candidate
    return None



# =====================================================
# COMPARE FUNCTION
# =====================================================
def compare_folders_verbose(
    folder_a,
    folder_b,
    find_string="",
    replace_string="",
    zip_search=False
    ):
    
    """
    Strict comparison:
    - relative path from A (after replace) MUST exist in B
    - optional ZIP inspection only if path points to a .zip
    """

    files_a = list_files_in_folder(folder_a)

    counters = {
        'processed': 0,
        'found': 0,
        'missing': 0,
        'found_in_zip': 0,
    }

    missing = []
    present = []

    for rel in files_a:
        counters['processed'] += 1

        diag.info("=" * 60)
        diag.info(f"File [{counters['processed']}]: {rel}")

        # --- normalize + version replace
        mapped_rel = normalize_path_for_compare(rel, find_string, replace_string)
        mapped_rel = mapped_rel.replace("\\", "/")
        diag.info(f"Mapped relative path: {mapped_rel}")

        # --- STRICT relative-path match in B
        candidate = os.path.join(folder_b, mapped_rel)

        if os.path.exists(candidate):
            diag.info(f"[OK] Found by relative path: {candidate}")
            counters['found'] += 1
            present.append(rel)
            continue

        found_in_zip = False

        if zip_search:
            parts = mapped_rel.split("/")

            for i, part in enumerate(parts):
                if part.lower().endswith(".zip"):
                    zip_path = os.path.join(folder_b, *parts[:i + 1])
                    inner_path = "/".join(parts[i + 1:]) if i + 1 < len(parts) else None

                    diag.info(f"Checking ZIP: {zip_path}, inner={inner_path}")

                    if inner_path and os.path.exists(zip_path):
                        if file_in_zip(zip_path, inner_path):
                            diag.info(f"[OK] Found inside ZIP: {zip_path} -> {inner_path}")
                            counters['found'] += 1
                            counters['found_in_zip'] += 1
                            present.append(rel)
                            found_in_zip = True
                            break
        else:
            diag.info("ZIP search disabled")

        if not found_in_zip:
            diag.info("[MISSING] No strict match (path or ZIP)")
            counters['missing'] += 1
            missing.append(rel)

    diag.info("=" * 60)
    diag.info(
        f"Summary: processed={counters['processed']}, "
        f"found={counters['found']} (zip={counters['found_in_zip']}), "
        f"missing={counters['missing']}"
    )

    # =================================================
    # RESULT FILES
    # =================================================
    name_a = os.path.basename(os.path.normpath(folder_a))
    name_b = os.path.basename(os.path.normpath(folder_b))

    missing_filename = f"{name_a}_not_in_{name_b}.txt"
    present_filename = f"common_{name_a}__{name_b}.txt"
    extra_filename   = f"{name_b}_not_in_{name_a}.txt"

    # --- missing
    with open(missing_filename, "w", encoding="utf-8") as f:
        for rel in sorted(missing):
            f.write(rel + "\n")

    # --- present
    with open(present_filename, "w", encoding="utf-8") as f:
        for rel in sorted(present):
            f.write(rel + "\n")

    # --- extra in B (STRICT by relative path)
    files_b = list_files_in_folder(folder_b)
    a_rel_set = set(
        normalize_path_for_compare(r, find_string, replace_string).replace("\\", "/")
        for r in files_a
    )

    extra = []
    for rel_b in files_b:
        rel_b_norm = rel_b.replace("\\", "/")
        if rel_b_norm not in a_rel_set:
            extra.append(rel_b)

    with open(extra_filename, "w", encoding="utf-8") as f:
        for rel in sorted(extra):
            f.write(rel + "\n")

    return missing, present, extra, counters

# =================================================
# RENAME LOg FILES
# =================================================
def rename_logs(build_A: str, build_B: str):
    if not build_A or not build_B:
        logging.info("Skipping log rename – version not detected")
        return

    prefix = f"{build_A}__{build_B}"

    mapping = {
        "compare_folders.log": f"{prefix}__compare_folders.log",
        "summary.log": f"{prefix}__summary.log",
        "diagnostic.log": f"{prefix}__diagnostic.log",
    }

    # zamknij handlery (Windows!)
    logging.shutdown()

    for src, dst in mapping.items():
        if os.path.exists(src):
            try:
                os.replace(src, dst)  # atomic rename
            except Exception as e:
                print(f"Failed to rename {src} -> {dst}: {e}")

# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    args = parse_args()
    logging.info(f"ZIP search enabled: {args.zip_search}")

    if args.folders_file:
        A, B = get_folders_from_file(args.folders_file)
    elif args.folder_a and args.folder_b:
        A, B = args.folder_a, args.folder_b
    else:
        print("You must specify either --folders_file or both --folder_a and --folder_b")
        sys.exit(1)

    if not os.path.exists(A):
        logging.error(f"Folder A does not exist: {A}")
        sys.exit(1)
    if not os.path.exists(B):
        logging.error(f"Folder B does not exist: {B}")
        sys.exit(1)

    build_A = extract_build(A)
    build_B = extract_build(B)

    if build_A and build_B:
        log_prefix = f"{build_A}__{build_B}"
    else:
        log_prefix = "NO_VERSION"

    if build_A and build_B:
        find_string = build_A
        replace_string = build_B
        logging.info(f"Auto-detected version mapping: {find_string} -> {replace_string}")
    else:
        find_string = ""
        replace_string = ""
        logging.info("No version numbers detected. Comparing files as-is.")

    missing_files, present_files, extra_files, counters = compare_folders_verbose(
        A,
        B,
        find_string,
        replace_string,
        zip_search=args.zip_search
        )

    summary_lines = [
    "==== Summary Report ====",
    f"A = {A}",
    f"B = {B}",
    ]

    if find_string and replace_string:
        summary_lines.append(
            f"Automatic replacement applied: '{find_string}' -> '{replace_string}'"
        )

    summary_lines.extend([
        f"Total files in A: {len(list_files_in_folder(A))}",
        f"Files missing in B: {len(missing_files)}",
        f"Files found in B: {len(present_files)}",
        f"Extra files in B: {len(extra_files)}",
    ])

    for line in summary_lines:
        logging.info(line)   # do plików
        #print(line)          # ZAWSZE do konsoli

    rename_logs(build_A, build_B)
