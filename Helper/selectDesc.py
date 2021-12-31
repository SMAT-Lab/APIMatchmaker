import threadpool
from Naked.toolshed.shell import *
import json
import pandas as pd

ANDROZOO_CSV_PATH = "/mnt/fit-Knowledgezoo/Patrick/latest/latest.csv"
NEW_PATH = "/home/username/APIRecommendation/Desc2000/"
TOTAL = 2000
COUNT = 0
sha256_pkg_map = {}


def get_pkg_map(csv_path):
    count = 0
    df = pd.read_csv(csv_path, header=0, chunksize=10000)
    for chunk in df:
        for i in range(len(chunk)):
            sha256 = chunk.iloc[i]['sha256']
            pkg = chunk.iloc[i]['pkg_name'].strip('\" ')
            market = chunk.iloc[i]['markets']
            if "play.google.com" in market:
                count += 1
                sha256_pkg_map[sha256] = pkg
            elif count >= TOTAL:
                return
    print("Collect package names successfully!")


def getAppNameWithTitle(output):
    if output[11] == '"':
        endQuotePos = output.find('"', 12)
        name = output[12: endQuotePos]
        if endQuotePos == 12:
            print("name is empty string")
    else:
        name = None
    return name


def process_one(sha256, p):
    global COUNT
    if COUNT > TOTAL:
        return
    outputpath = os.path.join(NEW_PATH, sha256 + ".csv")
    if os.path.exists(outputpath):
        COUNT += 1
        return
    noAPK = False
    # Run getMetaData.js
    metadata = 'node getMetadata.js ' + p
    metadataResult = ""
    response = muterun(metadata)
    try:
        if response.exitcode == 0:
            metadataResult = response.stdout
            testError = metadataResult.decode('utf-8')
            if testError[:5] == 'Error':
                endPos = testError.find('\n')
                print("Fail get metadata " + p + ". " + testError[:endPos])
                noAPK = True
            else:
                print("Succcessfully get metadata " + p)
        else:
            print(response.exitcode)
            print("Fail get metadata" + p)
            noAPK = True
    except:
        standard_err = response.stderr
        exit_code = response.exitcode
        print('Exit Status ' + str(exit_code) + ': ' + standard_err)

    # Write output
    if not noAPK:
        metadataOutput = metadataResult.decode('utf-8')
        metadataOutput = metadataOutput.replace("[Object]", "[]")
        metadataOutput = metadataOutput.replace("\n", '')
        metadataOutput = metadataOutput.replace("...", "")
        metadataOutput = metadataOutput.replace("more", "")
        metadataOutput = metadataOutput.replace("items", "")
        metadataOutput = metadataOutput.replace("item", "")

        name = getAppNameWithTitle(metadataOutput)
        # Check that metadata is not Type Error
        if metadataOutput[0:9] == "TypeError":
            name = None
        if name:
            metadataOutput = json.loads(metadataOutput)
            if "description" in metadataOutput and "score" in metadataOutput:
                description = metadataOutput["description"]
                score = metadataOutput['score']
                if score < 4:
                    return
                try:
                    with open(outputpath, "w", encoding='utf-8') as fw:
                        fw.write(description)
                    COUNT += 1
                    print("Successfully write metadata " + p)
                except Exception as e:
                    print(e)
                    print("Fail to write to output.")

        else:
            print("Could not write " + p + " as name is None (App not found on google.)")


if __name__ == '__main__':

    if not os.path.exists(NEW_PATH):
        os.mkdir(NEW_PATH)

    get_pkg_map(ANDROZOO_CSV_PATH)

    # Run the metadata javascript file
    for sha256 in sha256_pkg_map:
        process_one(sha256, sha256_pkg_map[sha256])
