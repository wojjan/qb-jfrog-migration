import subprocess
import sys
import argparse
import logging
import time
import re
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.sax.saxutils import escape


# ====== Logging ======
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("download_folder.log", encoding="utf-8", mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)

error_logger = logging.getLogger("errors")
fh = logging.FileHandler("errors.log", encoding="utf-8", mode="a")
fh.setLevel(logging.ERROR)
error_logger.addHandler(fh)

# Regex
saving_re = re.compile(r"Saving to:")
percent_re = re.compile(r"(\d+)%")       # wget progres


def download_with_wget(local_dir, base_url, username, password):

    cmd = [
        "wget", "-r", "-np", "-nH", "--cut-dirs=1",
        "--user", username, "--password", password,
        "-c",
        "--retry-connrefused", "--tries=3", "--waitretry=5",
        "-P", local_dir, base_url,
        "--reject", "index.html"
    ]

    # ===== XML =====
    root = Element("DownloadSession", start=time.strftime("%Y-%m-%dT%H:%M:%S"))
    start_node = SubElement(root, "StartDownload")
    SubElement(start_node, "url").text = base_url
    SubElement(start_node, "output_dir").text = local_dir
    SubElement(start_node, "command").text = " ".join(cmd)

    logging.info("⬇ Start download...")

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, bufsize=1)

    full_log = open("download_raw.log", "a", encoding="utf-8")

    file_count = 0                # ile plików wykryto
    current_file = None
    failed_files = []
    last_progress = time.time()


    # ===== STREAM z wget =====
    for line in iter(process.stderr.readline, ''):
        line = line.strip()
        full_log.write(line + "\n")

        # ------------------- Nowy plik --------------------
        if line.startswith("Saving to:"):
            m = re.search(r"Saving to: '(.+)'", line)
            current_file = m.group(1) if m else line.replace("Saving to:", "").strip()

            file_count += 1
            print(f"\r📥 [{file_count}] {current_file}                          ",
                  end="", flush=True)
            logging.info(f"[{file_count}] -> {current_file}")


        # ------------------- Progress ---------------------
        m = percent_re.search(line)
        if m and time.time() - last_progress > 1:
            print(f"\r⏳ {m.group(1)}% | 📄[{file_count}] {current_file}   ",
                  end="", flush=True)
            last_progress = time.time()


        # ------------------- Błędy ------------------------
        # Sprawdzenie błędów wget, ale nie nazw plików
            if ("error" in line.lower() and "Saving to" not in line) or \
               "failed:" in line.lower() or \
           "404" in line:

                err = f"[{current_file}] {line}"
                failed_files.append(err)
                error_logger.error(err)

                e = SubElement(root, "Error")
                e.text = escape(err)

                print(f"\n❌ ERROR in file [{file_count}] {current_file} → log saved")


    stdout, stderr = process.communicate()
    full_log.close()

    # ===== XML wynik =====
    result = SubElement(root, "WgetResult")
    SubElement(result, "returncode").text = str(process.returncode)
    SubElement(result, "stdout").text = escape((stdout or "").strip())
    SubElement(result, "stderr").text = escape((stderr or "").strip())
    SubElement(result, "files_downloaded").text = str(file_count)

    if failed_files:
        f_node = SubElement(root, "FailedFiles")
        for f in failed_files:
            SubElement(f_node, "file").text = escape(f)

    with open("download.xml", "wb") as f:
        f.write(tostring(root, encoding="utf-8"))


    print(f"\n\n📦 TOTAL files processed: {file_count}")
    if failed_files:
        print(f"⚠ Failed files: {len(failed_files)} | see errors.log & download.xml")
    else:
        print("✅ Finished without errors")


# ===== Helpers =====
def load_file_1line(path):
    return open(path, "r", encoding="utf-8").read().strip()

def load_login_data(path="jenkins-login.txt"):
    u, p = open(path, "r", encoding="utf-8").read().splitlines()[:2]
    return u.strip(), p.strip()

def load_args_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        a, b = [x.strip() for x in f if x.strip()][:2]
        return a, b


# ===== Main =====
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("local_dir", nargs="?")
    parser.add_argument("base_url", nargs="?")
    parser.add_argument("--args_file")
    parser.add_argument("--login_file")
    args = parser.parse_args()

    if args.args_file:
        local_dir, base_url = load_args_from_file(args.args_file)
    else:
        local_dir = args.local_dir
        base_url = args.base_url

    if args.login_file:
        username, password = load_login_data(args.login_file)
    else:
        username = load_file_1line("username.txt")
        password = load_file_1line("token.txt")

    download_with_wget(local_dir, base_url, username, password)
