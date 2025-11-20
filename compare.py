import os
import zipfile
import logging
import sys

# Configure logging to both file and screen
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("compare_folders.log", mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

def list_files_in_folder(folder, counters):
    files = []
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, folder)
            if filename.lower().endswith('.zip'):
                with zipfile.ZipFile(full_path, 'r') as z:
                    for zipinfo in z.infolist():
                        if not zipinfo.is_dir():
                            files.append(os.path.join(rel_path, zipinfo.filename))
                            counters['unpacked'] += 1
                            logging.info(f"Unpacked from zip: {os.path.join(rel_path, zipinfo.filename)}")
            else:
                files.append(rel_path)
    return files

def compare_folders(folder_a, folder_b):
    counters = {'processed': 0, 'found': 0, 'unpacked': 0, 'missing': 0}
    missing = []
    files_a = list_files_in_folder(folder_a, counters)
    for rel in files_a:
        counters['processed'] += 1
        target = os.path.join(folder_b, rel)
        if not os.path.exists(target):
            parts = rel.split(os.sep)
            found = False
            for i in range(len(parts)):
                if parts[i].lower().endswith('.zip'):
                    zip_path = os.path.join(folder_b, *parts[:i+1])
                    inner_file = os.path.join(*parts[i+1:])
                    if os.path.exists(zip_path):
                        with zipfile.ZipFile(zip_path, 'r') as z:
                            if inner_file in z.namelist():
                                logging.info(f"Present in zip: {rel}")
                                counters['found'] += 1
                                found = True
                                break
            if not found:
                logging.warning(f"Missing: {rel}")
                counters['missing'] += 1
                missing.append(rel)
        else:
            logging.info(f"Present: {rel}")
            counters['found'] += 1
    return missing, counters

if __name__ == "__main__":
    A = r"C:\repository\qb-jenkins-migration\download-jenkins\pact_sps_prod-igk-local\SPS-5.0\EagleStream-R\MAIN\SPS_E5_06.01.04.211.0"
    B = r"C:\repository\qb-jenkins-migration\download-qb\SPS_E5_06.01.04.211.0"

    missing_files, counters = compare_folders(A, B)

    logging.info("==== Summary Report ====")
    logging.info(f"Total files processed: {counters['processed']}")
    logging.info(f"Files found: {counters['found']}")
    logging.info(f"Files unpacked from zip: {counters['unpacked']}")
    logging.info(f"Files missing: {counters['missing']}")

    if missing_files:
        logging.warning("Missing files:")
        for f in missing_files:
            logging.warning("  " + f)
    else:
        logging.info("All files from A exist in B!")
