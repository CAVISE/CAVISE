#!/usr/bin/env python3

import os
import sys
import re
import logging
import argparse
from git import Repo, cmd
from git.exc import GitCommandError, InvalidGitRepositoryError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def get_available_versions(repo_url):
    logger.info(f"Getting repo versions: {repo_url}...")
    try:
        git = cmd.Git()
        refs_output = git.ls_remote("--heads", "--tags", repo_url).strip()

        versions = []
        tag_pattern = r'refs/tags/(.+?)$'
        for match in re.finditer(tag_pattern, refs_output, re.MULTILINE):
            tag_name = match.group(1)
            versions.append(("tag", tag_name))

        branch_pattern = r'refs/heads/(.+?)$'
        for match in re.finditer(branch_pattern, refs_output, re.MULTILINE):
            branch_name = match.group(1)
            versions.append(("branch", branch_name))

        return versions
    except GitCommandError as e:
        logger.error(f"Cannot get repo version from {repo_url}: {e}")
        return []


def select_version_interactive(repo_name, repo_url):
    versions = get_available_versions(repo_url)

    if not versions:
        raise ValueError('Cannot get repo versions. Please check your local repository or try to clone it again.')

    print(f"{repo_name} versions:")
    for i, (ref_type, version) in enumerate(versions, 1):
        print(f"{i}. [{ref_type}] {version}")

    while True:
        try:
            choice = input(f"Choose version: (1-{len(versions)}): ").strip()
            choice_num = int(choice)
            if 1 <= choice_num <= len(versions):
                selected = versions[choice_num - 1][-1]
                break
            else:
                print(f"Choose from 1 to {len(versions)}")
        except ValueError:
            print("Wrong value, try one more time")
    return selected


def clone_repo(repo_base, repo_name, version):
    repo_url = f"{repo_base}{repo_name}"
    if os.path.isdir(repo_name):
        logger.info(f"Repository {repo_name} already exists. Skipping.")
        return

    clone_msg = f"Cloning {repo_url}"
    if version:
        clone_msg += f" (version: {version})"
    logger.info(f"{clone_msg}...")

    try:
        if version:
            Repo.clone_from(repo_url, repo_name, recursive=True, branch=version)
        else:
            Repo.clone_from(repo_url, repo_name, recursive=True)
        logger.debug(f"Successfully cloned {repo_url}")
    except GitCommandError as e:
        logger.error(f"Failed to clone {repo_url}: {e}")
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--opencda-version",
        type=str,
        help="Version (branch or tah) for opencda. Default: main",
    )
    parser.add_argument(
        "-a", "--artery-version",
        type=str,
        help="Version (branch or tah) for artery. Default: main",
    )
    parser.add_argument(
        "repos",
        nargs="*",
        choices=["opencda", "artery"],
        help="Repos for cloning. Default: all",
    )
    
    args = parser.parse_args()
    return args

def main():
    args = parse_args()

    try:
        repo = Repo(".")
        origin_url = repo.remotes.origin.url
        repo_base = origin_url.rsplit("/", 1)[0] + "/"
    except InvalidGitRepositoryError:
        logger.error("Current directory is not a Git repository")
        sys.exit(1)
    except AttributeError:
        logger.error("No origin remote found")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error determining repo base URL: {e}")
        sys.exit(1)

    repos = args.repos if args.repos else ["opencda", "artery"]
    logger.info(f"Repositories to process: {repos}")

    for repo_name in repos:
        if repo_name == "opencda":
            version = args.opencda_version
        elif repo_name == "artery":
            version = args.artery_version
        else:
            version = None

        if version is None:
            repo_url = f"{repo_base}{repo_name}"
            version = select_version_interactive(repo_name, repo_url)

        clone_repo(repo_base, repo_name, version)

    logger.info("Operation completed successfully")


if __name__ == "__main__":
    main()
