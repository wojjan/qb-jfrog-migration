# QB–JF Build Comparison Tools

This repository contains Python (.py) and Windows batch (.bat) utilities used to compare
**JFrog (jf) builds** against **Quick Build (qb) builds**.

The **Quick Build (qb)** output is treated as the **reference build**.
The **JFrog (jf)** output is the build being validated.
These tools support verification of the **qb → jf migration process**.


## compare.py

### Purpose

The `compare.py` script compares two build directories and reports:
- files common to both builds
- files missing in the JFrog build
- extra files present only in the JFrog build

ZIP archives are supported and inspected internally.


### Usage

Run the comparison using Python:

python.exe c:/repository/qb-jenkins-migration/compare.py ^
  --folders_file c:/repository/qb-jenkins-migration/compare-input-files.txt


## Input File Format

The file provided via `--folders_file` must contain **two absolute paths**, one per line:

C:\repository\qb-jenkins-migration\download-qb\EagleStream-R\SPS_E5_06.01.04.226.0
C:\repository\qb-jenkins-migration\download-jenkins\pact_sps_prod-igk-local\SPS-5.0\EagleStream-R\SPS_E5_06.00.05.150.0

Path meaning:
- Line 1: Quick Build (qb) directory — reference build
- Line 2: JFrog (jf) directory — build under comparison


## Output Files

Each comparison generates **six output files**.


### Log Files

06.01.04.226.0__06.00.05.150.0__compare_folders.log
06.01.04.226.0__06.00.05.150.0__diagnostic.log
06.01.04.226.0__06.00.05.150.0__summary.log

Description:
- compare_folders.log  — main comparison process log
- diagnostic.log       — detailed per-file diagnostics
- summary.log          — high-level comparison summary


### Result Files

common_SPS_E5_06.01.04.226.0__SPS_E5_06.00.05.150.0.txt
SPS_E5_06.00.05.150.0_not_in_SPS_E5_06.01.04.226.0.txt
SPS_E5_06.01.04.226.0_not_in_SPS_E5_06.00.05.150.0.txt

Meaning:
- common_*.txt  
  Files present in both qb and jf builds

- <jf>_not_in_<qb>.txt  
  Files present in the JFrog build but missing from the Quick Build

- <qb>_not_in_<jf>.txt  
  Files present in the Quick Build but missing from the JFrog build  
  **This is the most important comparison result**


## Notes

- Build version numbers are automatically detected and mapped
- ZIP archives are inspected without extraction
- Comparison is based on normalized relative paths and filenames
- Designed for large build trees and migration validation
