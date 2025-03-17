#!/usr/bin/env python3

import os
import subprocess
import sys


def clone_repo(repo_base, repo):
    repo_full_path = repo_base + repo
    if os.path.isdir(repo):
        print(f"Repository {repo} already exists. Skipping.")
    else:
        print(f"Cloning {repo_full_path}...")
        try:
            subprocess.run(["git", "clone", "--recurse-submodules", f"{repo_full_path}"], check=True)
        except subprocess.CalledProcessError:
            sys.exit(f"Error: Unable to clone repo {repo_full_path}.")


if __name__ == "__main__":
    try:
        repo_base = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip()
        repo_base = repo_base.rsplit("/", 1)[0] + "/"
    except subprocess.CalledProcessError:
        sys.exit("Error: Unable to determine repo base URL.")

    print(f"Repo base URL: {repo_base}")

    all_repos = ["opencda", "artery", "scenario-manager"]
    repos = sys.argv[1:] if len(sys.argv) > 1 else all_repos

    print(f"Repositories to process: {repos}")

    for repo in repos:
        clone_repo(repo_base, repo)

    print("Operation completed!")
