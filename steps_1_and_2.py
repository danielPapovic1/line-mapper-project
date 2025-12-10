import os
import zipfile
import xml.etree.ElementTree as ET


# OPTIONAL HELPER FUNCTION FOR ZIP EXTRACTION
def extract_if_needed(zip_path="EvaluationDataset.zip", extract_to="evaluations"):
    # Create output folder if it does not exist
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    # If folder is already filled, skip extraction
    if len(os.listdir(extract_to)) > 0:
        print("[INFO] Dataset already extracted.")
        return

    # Extract only if the ZIP exists
    if os.path.exists(zip_path):
        print(f"[INFO] Extracting {zip_path} → {extract_to} ...")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_to)
        print("[INFO] Extraction complete.\n")
    else:
        print(f"[WARNING] ZIP file '{zip_path}' was not found. Extraction skipped.")

# STEP 1 — File Loading + Preprocessing
def load_file(path):
   #open file in text mode, ignoring encoding errors
    with open(path, "r", encoding="utf8", errors="ignore") as f:
        lines = f.readlines() #Read entire file into list of lines

    cleaned = []
    #Loop through each line in the file
    for line in lines:
        line = line.strip()   #Remove leading/trailing whitespace
        if line:    #Skip blank lines
            cleaned.append(line)
    #Returns list of cleaned lines
    return cleaned

# STEP 2 — Ground Truth XML Loader
def load_ground_truth(xml_path):
    #Load and parse the XML file in tree structure
    tree = ET.parse(xml_path)
    #Get the root element of the XML
    root = tree.getroot()

    mapping = {}
    #Loop through each location element in the XML
    for loc in root.findall(".//LOCATION"):
        old_line = int(loc.attrib["ORIG"])  #Origina line number
        new_line = int(loc.attrib["NEW"]) #New line number
        mapping[old_line] = new_line #Store in mapping dictionary
    #Return mapping dictionary
    return mapping
