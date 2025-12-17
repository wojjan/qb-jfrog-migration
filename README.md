# QB–JF Build Comparison Tools

This repository contains Python (`.py`) and Windows batch (`.bat`) scripts used to compare **JFrog (jf) builds** against **Quick Build (qb) builds**.

The **Quick Build (qb)** output is treated as the **reference build**, while the **JFrog (jf)** build is the one being verified.  
These tools support validation of the **qb → jf migration process**.

---

## compare.py – Usage

Run the comparison script using Python:

```bash
python.exe c:/repository/qb-jenkins-migration/compare.py ^
  --folders_file c:/repository/qb-jenkins-migration/compare-input-files.txt


Input file format

The file specified by --folders_file must contain two paths, one per line:
```bash
C:\repository\qb-jenkins-migration\download-qb\EagleStream-R\SPS_E5_06.01.04.226.0
C:\repository\qb-jenkins-migration\download-jenkins\pact_sps_prod-igk-local\SPS-5.0\EagleStream-R\SPS_E5_06.00.05.150.0


Line 1: Quick Build (qb) directory — reference build

Line 2: JFrog (jf) directory — build under comparison

Output Files

Each comparison produces six output files.

Log files
```bash
06.01.04.226.0__06.00.05.150.0__compare_folders.log
06.01.04.226.0__06.00.05.150.0__diagnostic.log
06.01.04.226.0__06.00.05.150.0__summary.log


compare_folders.log – main comparison log

diagnostic.log – detailed per-file diagnostics

summary.log – high-level summary of the comparison

Result files
```bash
common_SPS_E5_06.01.04.226.0__SPS_E5_06.00.05.150.0.txt
SPS_E5_06.00.05.150.0_not_in_SPS_E5_06.01.04.226.0.txt
SPS_E5_06.01.04.226.0_not_in_SPS_E5_06.00.05.150.0.txt


common_*.txt
Files present in both qb and jf builds

<jf>_not_in_<qb>.txt
Files present in the JFrog build but missing from the Quick Build

<qb>_not_in_<jf>.txt
Files present in the Quick Build but missing from the JFrog build
This is the most important result of the comparison

Notes

Build version numbers are automatically detected and mapped.

ZIP files are supported and inspected internally.

The comparison is based on normalized relative paths and filenames.
