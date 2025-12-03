import subprocess
import sys
import argparse
import logging

# Configure logging to both file and screen
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("download_folder.log", mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)

def download_with_wget(local_dir, base_url, username, password):
    url = base_url  # lub aktualny URL z pętli

    cmd = [
        "wget", "-d", "-r", "-np", "-nH", "--cut-dirs=1",
        "--user", username,
        "--password", password,
        "-P", local_dir,
        url
    ]

    # --- LOGI PRZED WYWOŁANIEM ---
    logging.error(f"Running wget for URL: {url}")
    logging.error(f"Target local folder: {local_dir}")
    logging.error(f"Full command: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True
    )

    # --- LOGUJEMY WYJŚCIE Z wget ---
    logging.error("---- WGET STDOUT ----")
    logging.error(result.stdout)

    logging.error("---- WGET STDERR ----")
    logging.error(result.stderr)

    # --- jeśli error, rzucamy wyjątek (jak wcześniej) ---
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, cmd, output=result.stdout, stderr=result.stderr
        )



def load_token(path="c:\\repository\\qb-jenkins-migration\\token.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        logging.error(f"Plik {path} nie istnieje.")
        exit(1)


def load_username(path="c:\\repository\\qb-jenkins-migration\\username.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        logging.error(f"Plik {path} nie istnieje.")
        exit(1)


def load_login_data(path="c:\\repository\\qb-jenkins-migration\\jenkins-login.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            if len(lines) < 2:
                logging.error(
                    f"Argument file {path} must have at least 2 lines (username, token/password)."
                )
                exit(1)
            return lines[0], lines[1]
    except FileNotFoundError:
        logging.error(f"Argument file {path} does not exist.")
        exit(1)


def load_args_from_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            if len(lines) < 2:
                logging.error(
                    f"Argument file {path} must have at least 2 lines (local_dir, base_url)."
                )
                exit(1)
            return lines[0], lines[1]
    except FileNotFoundError:
        logging.error(f"Argument file {path} does not exist.")
        exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download files using wget with authentication.")
    parser.add_argument("local_dir", nargs="?", help="Local directory to save downloads")
    parser.add_argument("base_url", nargs="?", help="Base URL to download from")
    parser.add_argument("--args_file", help="Path to file containing arguments")
    parser.add_argument("--login_file", help="Path to file containing login data")
    args = parser.parse_args()

    if args.args_file:
        local_dir, base_url = load_args_from_file(args.args_file)
        logging.info(f"local_dir = {local_dir}")
        logging.info(f"base_url = {base_url}")

    if args.login_file:
        username, password = load_login_data(args.login_file)
    else:
        username = load_username()
        password = load_token()

        # If args_file not used, load CLI args
        if not args.args_file:
            local_dir = args.local_dir
            base_url = args.base_url

    download_with_wget(local_dir, base_url, username, password)
