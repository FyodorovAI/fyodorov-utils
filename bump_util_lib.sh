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
    PAUSE=90
    set +x
    echo "Waiting for $PAUSE seconds..."
    for ((i=$PAUSE; i>0; i--))
    do
        # -e  => enable interpretation of backslash escapes
        # -n  => do not output the trailing newline
        echo -en "\r\033[KCountdown: $i"
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
    FILE=${2:-Dockerfile}
    echo "Bumping and reinstalling lib in $DIRECTORY/requirements.txt to version $NEW_VERSION..."
    sed -i '' -E "s/fyodorov_utils==.*/fyodorov_utils==$NEW_VERSION/" $DIRECTORY/$FILE
    cd $DIRECTORY && git commit -a -m "bump utils lib to $NEW_VERSION" && git push
    cd $BASE
}

bump_and_reinstall $BASE/../Tsiolkovsky
bump_and_reinstall $BASE/../Gagarin
bump_and_reinstall $BASE/../Dostoyevsky
bump_and_reinstall $BASE README.md

date