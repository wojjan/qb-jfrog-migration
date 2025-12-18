# QB–JF Build Comparison Tools

This repository contains Python (`.py`) and Windows batch (`.bat`) scripts used to compare **JFrog (jf) builds** against **Quick Build (qb) builds**.

The **Quick Build (qb)** output is treated as the **reference build**, while the **JFrog (jf)** build is the one being verified.  
These tools support validation of the **qb → jf migration process**.

---

## compare.py – Usage

Run the comparison script using Python:

python.exe c:/repository/qb-jenkins-migration/compare.py ^
  --folders_file c:/repository/qb-jenkins-migration/compare-input-files.txt

Optional: enable searching inside ZIP archives:

python.exe c:/repository/qb-jenkins-migration/compare.py ^
  --folders_file c:/repository/qb-jenkins-migration/compare-input-files.txt ^
  --zip-search

ZIP search is **disabled by default**.

---

## Input File Format

The file specified by `--folders_file` must contain **two paths**, one per line:

C:\repository\qb-jenkins-migration\download-qb\EagleStream-R\SPS_E5_06.01.04.226.0  
C:\repository\qb-jenkins-migration\download-jenkins\pact_sps_prod-igk-local\SPS-5.0\EagleStream-R\SPS_E5_06.00.05.150.0  

Line 1: **Quick Build (qb)** directory — reference build  
Line 2: **JFrog (jf)** directory — build under comparison  

Alternatively, the reference build and the build under comparison can be provided directly using the `--folder_a` and `--folder_b` options, respectively.

---

## Output Files

Each comparison produces **six output files**.

### Log Files

<detected_folder_a_version>__<detected_folder_b_version>__compare_folders.log  
<detected_folder_a_version>__<detected_folder_b_version>__diagnostic.log  
<detected_folder_a_version>__<detected_folder_b_version>__summary.log  

<detected_folder_a_version>__<detected_folder_b_version>__compare_folders.log  
Main comparison log

<detected_folder_a_version>__<detected_folder_b_version>__diagnostic.log  
Detailed per-file diagnostics

<detected_folder_a_version>__<detected_folder_b_version>__summary.log  
High-level comparison summary

### Result Files

common_<detected_folder_a_version>__<detected_folder_b_version>__summary.txt  
<detected_folder_a_version>_not_<detected_folder_b_version>.txt  
<detected_folder_a_version>_not_in_<detected_folder_b_version>.txt  

common_<detected_folder_a_version>__<detected_folder_b_version>__summary.txt 
Files present in **both** qb and jf builds

<detected_folder_a_version>_not_<detected_folder_b_version>.txt 
Files present in the **JFrog build** but missing from the Quick Build

<detected_folder_a_version>_not_in_<detected_folder_a_version>.txt  
Files present in the **Quick Build** but missing from the JFrog build  
This is the **most important comparison result**.

---

## ZIP Search Behavior

By default, the comparison:

- Uses **strict relative path matching**
- Compares **filesystem content only**
- Does **not** inspect ZIP files

When `--zip-search` is enabled:

- ZIP archives are inspected **only when required**
- A file missing by path may still be found **inside a ZIP**
- ZIP hits are counted and reported separately

ZIP search is **optional and disabled by default** to avoid false positives and performance impact.

---

## Notes

- Build version numbers are **automatically detected and mapped**
- Version replacement is applied only when versions are detected
- Path comparison uses **normalized relative paths**
- Logs are automatically renamed using detected build versions
