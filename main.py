#!/usr/bin/env python3

from pkg_resources import resource_listdir
import requests
import json
import sys

SPOTBUGS_TOOL_ID = "db4f1048-70d9-439e-b8a7-85a8dd91858c"
SPOTBUGS_TOOL_NAME = "spotbugs"


def getCodePatterns(toolId):
    headers = {
        'Accept': 'application/json'
    }
    url = "https://app.codacy.com/api/v3/tools/%s/patterns?limit=1000" % toolId
    r = requests.get(url, headers=headers)
    response = json.loads(r.text)
    return response["data"]


def findPattern(key, patterns):
    pattern = [item for item in patterns if item.get('id') == key]
    if len(pattern) > 0:
        return pattern[0]
    else:
        return None


def generatePayloadResults(resultsDict):
    results = []
    for key in resultsDict:
        results.append({
            "filename": key,
            "results": resultsDict[key]["results"]
        })
    return results


def postToCodacy(provider, org, repo, commitUuid, projectToken, payload):
    headers = {
        'Accept': 'application/json',
        'project-token': projectToken
    }
    url = "https://api.codacy.com/2.0/%s/%s/%s/commit/%s/issuesRemoteResults" % (
        provider, org, repo, commitUuid)
    r = requests.post(url, headers=headers, data=payload)
    print(r)
    return

def triggerAnalysis(commitUuid,projectToken):
    headers = {
        'Accept': 'application/json',
        'project-token': projectToken
    }
    url = "https://api.codacy.com/2.0/commit/%s/resultsFinal"%commitUuid
    r = requests.post(url, headers=headers)
    print(r)

def main():
    filepath = None
    provider = None
    org = None
    repo = None
    commitUuid = None
    projectToken = None
    if len(sys.argv) < 7:
        raise Exception(
            "Usage is python3 main.py PATH_TO_FILE PROVIDER ORG REPO COMMIT_UUID PROJECT_TOKEN")
    else:
        filepath = sys.argv[1]
        provider = sys.argv[2]
        org = sys.argv[3]
        repo = sys.argv[4]
        commitUuid = sys.argv[5]
        projectToken = sys.argv[6]
    patterns = getCodePatterns(SPOTBUGS_TOOL_ID)
    resultsDict = {}
    file = open(filepath, 'r')
    lines = file.readlines()
    for line in lines:
        obj = json.loads(line)
        if obj["file"] not in resultsDict:
            resultsDict[obj["file"]] = {"results": []}
        pattern = findPattern(obj["patternId"], patterns)
        level = "Warning"
        category = None
        if pattern:
            level = pattern["level"]
            category = pattern["category"]
        resultsDict[obj["file"]]["results"].append({
            "Issue": {
                "patternId": {
                    "value": obj["patternId"]
                },
                "filename": obj["file"],
                "message": {
                    "text": obj["message"]
                },
                "level": level,
                "category": category,
                "location": {
                    "LineLocation": {
                        "line": obj["line"]
                    }
                }
            }
        })

    payload = [
        {
            "tool": SPOTBUGS_TOOL_NAME,
            "issues": {
                "Success": {
                    "results": generatePayloadResults(resultsDict)
                }

            }
        }
    ]
    postToCodacy(provider, org, repo, commitUuid, projectToken, payload)
    triggerAnalysis(commitUuid, projectToken)
    print(json.dumps(payload, indent=2))
    return


main()
