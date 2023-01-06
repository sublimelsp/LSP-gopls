#!/bin/bash

# Set the URL for the GitHub API
url="https://api.github.com/repos/golang/tools/tags"

# Call the GitHub API and retrieve the tags
tags=$(curl -s $url)

# Find the latest tag that matches the regex pattern
latest_tag=$(echo $tags | grep -o "gopls/v[0-9]\+\.[0-9]\+\.[0-9]\+" | sort -V | tail -1)

# Remove the prefix "gopls/" from the latest tag
latest_tag=${latest_tag#"gopls/"}

echo "$latest_tag"
