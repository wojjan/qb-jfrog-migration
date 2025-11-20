import os

def compare_folders(folder_a, folder_b):
    missing = []

    for root, _, files in os.walk(folder_a):
        for file in files:
            rel = os.path.relpath(os.path.join(root, file), folder_a)
            target = os.path.join(folder_b, rel)
            if not os.path.exists(target):
                missing.append(rel)
            else:
                print(f"found: {file}")

    return missing

if __name__ == "__main__":
    A = r"C:\repository\qb-jenkins-migration\download-jenkins\pact_sps_prod-igk-local\SPS-5.0\EagleStream-R\MAIN\SPS_E5_06.01.04.211.0"
    B = r"C:\repository\qb-jenkins-migration\download-qb\SPS_E5_06.01.04.211.0"

    missing_files = compare_folders(A, B)

    if missing_files:
        print("Missing files:")
        for f in missing_files:
            print("  " + f)
    else:
        print("All files from A exist in B!")
