# QB–JF Build Comparison Tools

This repository contains Python (`.py`) and Windows batch (`.bat`) scripts used to compare **JFrog (jf) builds** against **Quick Build (qb) builds**.

The **Quick Build (qb)** output is treated as the **reference build**, while the **JFrog (jf)** build is the one being verified.  
These tools support validation of the **qb → jf migration process**.  

The comparison process consists of three stages:

1. Manually download the required **qb** build. Just navigate to the remote qb build, download the Artifactory zip and unpack it locally.
2. Download the required **jf** build using the batch scripts:  
   a. `jf-config.bat` – configure server access for your user and the specific Artifactory. Please edit this file with your user name and Artifactory token. This step is required once per user and Artifactory.
   b. `jf-dl.bat jf-dl.bat <local relative path>` – download the JFrog build. This step is repeated each compare cycle. Example:
   `jf-dl.bat jf-dl.bat SPS-5.0/Tatlow-PC/SPS_E3_06.00.03.060.0`
3. Compare the two builds using the Python script.  

## compare.py – Usage

Run the comparison script with Python:

python.exe c:/repository/qb-jenkins-migration/compare.py \
  --folders_file c:/repository/qb-jenkins-migration/compare-input-files.txt

Optional: enable searching inside ZIP archives:

python.exe c:/repository/qb-jenkins-migration/compare.py \
  --folders_file c:/repository/qb-jenkins-migration/compare-input-files.txt \
  --zip-search

**Note:** ZIP search is disabled by default.

---

## Input File Format

The file specified by `--folders_file` must contain **two paths**, one per line, for example:

C:\repository\qb-jenkins-migration\download-qb\EagleStream-R\SPS_E5_06.01.04.226.0  
C:\repository\qb-jenkins-migration\download-jenkins\pact_sps_prod-igk-local\SPS-5.0\EagleStream-R\SPS_E5_06.00.05.150.0  

- **Line 1:** Quick Build (**qb**) directory — reference build  
- **Line 2:** JFrog (**jf**) directory — build under comparison  

Alternatively, you can specify the reference and comparison builds directly using `--folder_a` and `--folder_b`.

---

## Output Files

Each comparison produces **six output files**:

### Log Files

- `<folder_A_version>__<folder_B_version>__compare_folders.log` – main comparison log  
- `<folder_A_version>__<folder_B_version>__diagnostic.log` – detailed per-file diagnostics  
- `<folder_A_version>__<folder_B_version>__summary.log` – high-level comparison summary  

### Result Files

- `common_<folder_A_version>__<folder_B_version>.txt` – files present in **both** qb and jf builds  
- `<folder_B_version>_not_in_<folder_A_version>.txt` – files present in **JFrog build** but missing from Quick Build  
- `<folder_A_version>_not_in_<folder_B_version>.txt` – files present in **Quick Build** but missing from JFrog build (**most important result**)  

---

## ZIP Search Behavior

By default, the comparison:

- Uses **strict relative path matching**  
- Compares **filesystem content only**  
- Does **not** inspect ZIP files  

When `--zip-search` is enabled:

- ZIP archives are inspected **only when necessary**  
- Files missing by path may still be found **inside ZIPs**  
- ZIP hits are counted and reported separately  

**Note:** ZIP search is optional and disabled by default to avoid false positives and performance issues.

---

## Notes

- Build version numbers are **automatically detected and mapped**  
- Version replacement is applied only when versions are detected  
- Path comparison uses **normalized relative paths**  
- Logs are automatically renamed using detected build versions
