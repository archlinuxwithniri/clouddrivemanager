#!/bin/bash

echo "==========================="
echo "      GOOGLE DRIVE LOBBY"
echo "==========================="

# Read all existing remotes from rclone config
REMOTES=$(rclone listremotes | sed 's/://')

if [ -z "$REMOTES" ]; then
    echo "No rclone remotes found."
    exit 1
fi

for D in $REMOTES; do
    echo
    echo "---- $D ----"

    # Run rclone about and capture JSON
    JSON=$(rclone about $D: --json 2>/dev/null)

    if [ -z "$JSON" ]; then
        echo "Error: Cannot access $D"
        continue
    fi

    # Extract values using jq
    TOTAL=$(echo "$JSON" | jq -r '.total')
    USED=$(echo "$JSON" | jq -r '.used')
    FREE=$(echo "$JSON" | jq -r '.free')
    OTHER=$(echo "$JSON" | jq -r '.other')

    # Convert bytes → human readable
    HTOTAL=$(numfmt --to=iec --suffix=B $TOTAL)
    HUSED=$(numfmt --to=iec --suffix=B $USED)
    HFREE=$(numfmt --to=iec --suffix=B $FREE)
    HOTHER=$(numfmt --to=iec --suffix=B $OTHER)

    # Display
    echo "Total:   $HTOTAL"
    echo "Used:    $HUSED"
    echo "Free:    $HFREE"
    echo "Other:   $HOTHER"
done

echo

