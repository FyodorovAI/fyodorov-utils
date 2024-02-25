#!/bin/bash

set -ex -o pipefail

BASE="$HOME/Projects/Fyodorov/fyodorov-llm-agents"
FILE="$BASE/pyproject.toml"

date
# Check if --upgrade flag is not passed
if [[ "$1" == "--upgrade" ]]; then
    echo "Reinstalling lib in all services to version $NEW_VERSION..."
else
    # Bump the version in pyproject.toml
    awk -F'=' -v OFS='=' '/^version =/ { split($2, a, "."); a[3]++; $2 = a[1] "." a[2] "." a[3] "\""; print; next } 1' $FILE > tmp && mv tmp $FILE
    # Run make release
    make release
    PAUSE=90
    echo "Waiting for $PAUSE seconds..."
    sleep $PAUSE
fi

# Extract the new version
NEW_VERSION=$(awk -F'"' '/^version =/ { print $2 }' $FILE)

# Function to bump version in requirements.txt and reinstall requirements
bump_and_reinstall() {
    DIRECTORY=$1
    echo "Bumping and reinstalling lib in $DIRECTORY/requirements.txt to version $NEW_VERSION..."
    sed -i '' -E "s/fyodorov_llm_agents==.*/fyodorov_llm_agents==$NEW_VERSION/" $DIRECTORY/requirements.txt
    source $DIRECTORY/venv/bin/activate && pip install --force-reinstall fyodorov_llm_agents==$NEW_VERSION && deactivate
}

bump_and_reinstall $BASE/../Tsiolkovsky/src
bump_and_reinstall $BASE/../Gagarin/src

date