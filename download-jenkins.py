import subprocess
import sys

def download_with_wget(local_dir, base_url, username, password):
    cmd = [
        "wget",
        "-r",
        "-np",
        "-nH",
        "--cut-dirs=1",
        f'--user={username}',
        f'--password={password}',
        "-P", local_dir,
        base_url
    ]
    print("Running command:", " ".join(cmd))
    subprocess.run(cmd, check=True)

def load_token(path="c:\\repository\\qb-jenkins-migration\\token.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"[ERROR] Plik {path} nie istnieje.")
        exit(1)

def load_username(path="c:\\repository\\qb-jenkins-migration\\username.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"[ERROR] Plik {path} nie istnieje.")
        exit(1)

def load_args_from_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            if len(lines) < 4:
                print(f"[ERROR] Argument file {path} must have at least 4 lines (local_dir, base_url, username, password).")
                exit(1)
            return lines[0], lines[1], lines[2], lines[3]
    except FileNotFoundError:
        print(f"[ERROR] Argument file {path} does not exist.")
        exit(1)


if __name__ == '__main__':
    # Usage:
    #   python script.py <local_dir> <base_url>
    #   python script.py --args-file <file_path>
    import argparse

    parser = argparse.ArgumentParser(description="Download files using wget with authentication.")
    parser.add_argument("local_dir", nargs="?", help="Local directory to save downloads")
    parser.add_argument("base_url", nargs="?", help="Base URL to download from")
    parser.add_argument("--args-file", help="Path to file containing arguments")
    args = parser.parse_args()

    if args.args_file:
        local_dir, base_url, username, password = load_args_from_file(args.args_file)
    else:
        local_dir = args.local_dir or "c:/repository/qb-jenkins-migration/download-jenkins"
        base_url = args.base_url or 'https://af01p-igk.devtools.intel.com/artifactory/pact_sps_prod-igk-local/SPS-5.0/EagleStream-R/MAIN/SPS_E5_06.01.04.211.0/'
        username = load_username()
        password = load_token()

    download_with_wget(local_dir, base_url, username, password)
