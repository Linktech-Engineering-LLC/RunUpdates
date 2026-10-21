#!/bin/bash

# Forgejo server info
FORGEJO_URL="http://dad:3000"
OWNER="Linux"
REPO="RunUpdates"
TOKEN="api-token"

echo "Fetching workflow runs for $OWNER/$REPO..."

# Get all run IDs
RUN_IDS=$(curl -s \
  -H "Authorization: token $TOKEN" \
  "$FORGEJO_URL/api/v1/repos/$OWNER/$REPO/actions/runs" \
  | jq -r '.runs[].id')

if [ -z "$RUN_IDS" ]; then
  echo "No workflow runs found."
  exit 0
fi

echo "Found runs:"
echo "$RUN_IDS"

echo
echo "Deleting runs..."
echo

for ID in $RUN_IDS; do
  echo -n "Deleting run $ID... "
  curl -s -X DELETE \
    -H "Authorization: token $TOKEN" \
    "$FORGEJO_URL/api/v1/repos/$OWNER/$REPO/actions/runs/$ID"
  echo "done"
done

echo
echo "All workflow runs deleted."
