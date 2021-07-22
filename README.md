# codacy-spotbugs-to-api

An helper that converts the output of Codacy/Spotbugs docker image and uploads it to Codacy.
Currently only available for Codacy SaaS.

## Usage
The `requirements.txt` lists all Python libraries that should be installed before running the script:

```bash
pip install -r requirements.txt
```

To run the script

```bash
python3 main.py PATH_TO_FILE_WITH_SPOTBUGS_ISSUES PROVIDER ORG REPO COMMIT_UUID PROJECT_TOKEN
```