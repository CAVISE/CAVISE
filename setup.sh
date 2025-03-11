#!/bin/bash

if [ -f "paths.conf" ]; then
    source paths.conf
else
    echo "Warning: paths.conf not found!"
fi

echo "CAVISE_ROOT=$CAVISE_ROOT"
echo "PATH_TO_ARTERY=$PATH_TO_ARTERY"
echo "PATH_TO_OPENCDA=$PATH_TO_OPENCDA"
echo "PATH_TO_SUMO=$PATH_TO_SUMO"
echo "PATH_TO_CARLA=$PATH_TO_CARLA"

repo_base="$(git remote get-url origin 2>/dev/null | sed -E 's|^(.*/)[^/]+\.git$|\1|')"
echo "Repo base URL: $repo_base"

all_repos="opencda artery scenario-manager"

if [ $# -eq 0 ]; then
    echo "No repositories specified. Cloning all defined repos."
    repos="$all_repos"
else
    repos="$@"
fi

echo "Repositories to process: ${repos}"

clone_repo() {
    local repo_base=$1
    local repo=$2

    if [ -d "$repo" ]; then
        echo "Repository $repo already exists. Skipping."
    else
        echo "Cloning $repo_base to $repo..."
        git clone --recurse-submodules "$repo_base$repo"
    fi
}

for repo in ${repos}; do
    clone_repo $repo_base $repo
done

echo "Operation completed!"