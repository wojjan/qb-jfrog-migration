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
