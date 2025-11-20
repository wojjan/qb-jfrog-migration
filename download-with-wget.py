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


if __name__ == '__main__':
    # Usage: python script.py <local_dir> <base_url>
    #local_dir = sys.argv[1]  # e.g., 'c:/repository/qb-jenkins-migration/download-jenkins'
    local_dir = "c:/repository/qb-jenkins-migration/download-jenkins"
    #base_url = sys.argv[2]   # e.g., 'https://af01p-igk.devtools.intel.com/artifactory/pact_sps_prod-igk-local/SPS-5.0/EagleStream-R/MAIN/SPS_E5_06.01.04.211.0/'
    base_url = 'https://af01p-igk.devtools.intel.com/artifactory/pact_sps_prod-igk-local/SPS-5.0/EagleStream-R/MAIN/SPS_E5_06.01.04.211.0/'

    TOKEN = load_token()
    username = "jwojdat"
    password = TOKEN
    download_with_wget(local_dir, base_url, username, password)
