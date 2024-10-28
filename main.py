import argparse
import json
import sys
import os
from nilsimsa import Nilsimsa

exceptions = [".cache", ".cython", "__pycache__"]

def extract_watchdog_to_json (watchdog_file:str, json_file:str):
    
    list_of_outputs = []

    with open (watchdog_file, 'r') as watchdog_f:
        # singletons = list(dict.fromkeys(watchdog_f.readlines()))
        
        singletons = []
        # Remove line breaks and space seperated multi-files
        for ifile in watchdog_f.readlines():
            ifile_to_add = ifile
            if "\n" in ifile_to_add:
                ifile_to_add = ifile_to_add.replace("\n", "")
            if " " in ifile_to_add:
                for isubfile in ifile_to_add.split(" "):
                    singletons.append (isubfile)
            else:
                singletons.append(ifile_to_add)

        # Remove duplicates
        singletons_all = list(dict.fromkeys(singletons))
        singletons = []
        # Remove exceptions
        for ifile in singletons_all:
            is_exception = False
            for iexception in exceptions:
                if iexception in ifile:
                    is_exception = True
            if not is_exception and ifile:
                singletons.append(ifile)

        # Remove remaining duplicates
        singletons = list(dict.fromkeys(singletons))
        
        for ifile in singletons:
            all_info = os.path.basename(ifile) + str(os.path.getsize(ifile))
            filehash = Nilsimsa(all_info).hexdigest()
            list_of_outputs.append({"url": None, "path": ifile, "hash": filehash, "size": os.path.getsize(ifile), "filename": os.path.basename(ifile)})

        
    json_content = None
    with open (json_file, 'r') as json_f:
        json_content = json.load(json_f)
        json_content["Outputs"] = list_of_outputs
    return json_content

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Extract watchdog list of files to HBP JSON metadata')
    parser.add_argument('--json', type=argparse.FileType('r'), metavar='json', nargs=1,
                        help='JSON File containing in which metadata of files are extracted', required=True)
    parser.add_argument('--watchdog', type=argparse.FileType('r'), metavar='watchdog', nargs=1,
                        help='Watchdog File containing files to extract to JSON report', required=True)


    args = parser.parse_args()
    
    json_file = args.json[0]
    watchdog_file = args.watchdog[0]

    # Convert watchdog list to JSON content
    json_content = extract_watchdog_to_json (watchdog_file.name, json_file.name)

    # Write JSON content to JSON file
    with open("watchdog_report.json", "w") as f:
        json.dump(json_content, f, indent=4) 
    # Exit Done ?
    sys.exit()