#/bin/bash

last_commit_sha=$(git rev-parse HEAD)
sed -i "s/thoth-github-action@.*/thoth-github-action@$last_commit_sha/g" ".github/workflows/test-action.yaml"
