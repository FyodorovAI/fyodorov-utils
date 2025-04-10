#!/bin/bash

set -ex -o pipefail

BASE="$HOME/Projects/Fyodorov/fyodorov_utils"
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
    PAUSE=120
    set +x
    echo "Waiting for $PAUSE seconds..."
    for ((i=$PAUSE; i>0; i--))
    do
        # -e  => enable interpretation of backslash escapes
        # -n  => do not output the trailing newline
        echo -en "\rCountdown: $i"
        sleep 1
    done

    # Move to a new line when done
    echo
    set -x
fi

# Extract the new version
NEW_VERSION=$(awk -F'"' '/^version =/ { print $2 }' $FILE)

# Function to bump version in requirements.txt and reinstall requirements
bump_and_reinstall() {
    DIRECTORY=$1
    FILE=${2:-requirements.txt}
    echo "Bumping and reinstalling lib in $DIRECTORY/requirements.txt to version $NEW_VERSION..."
    sed -i '' -E "s/fyodorov_utils==.*/fyodorov_utils==$NEW_VERSION/" $DIRECTORY/$FILE
    source $DIRECTORY/venv/bin/activate && pip install --force-reinstall fyodorov_utils==$NEW_VERSION && deactivate
}

bump_and_reinstall $BASE/../Tsiolkovsky/src
bump_and_reinstall $BASE/../Gagarin/src
bump_and_reinstall $BASE/../Dostoyevsky/src
bump_and_reinstall $BASE README.md

date