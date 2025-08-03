#!/usr/bin/env python3

import os
import sys
import logging
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

CAVISE_TAGS = {
    "opencda": "v1.0.0",
    "artery": None
}


def clone_repo(repo_base, repo_name, tag=None):
    repo_url = f"{repo_base}{repo_name}"
    if os.path.isdir(repo_name):
        logger.info(f"Repository {repo_name} already exists. Skipping.")
        return

    clone_msg = f"Cloning {repo_url}"
    if tag:
        clone_msg += f" (tag: {tag})"
    logger.info(f"{clone_msg}...")

    try:
        if tag:
            Repo.clone_from(repo_url, repo_name, recursive=True, branch=tag)
        else:
            Repo.clone_from(repo_url, repo_name, recursive=True)
        logger.debug(f"Successfully cloned {repo_url}")
    except GitCommandError as e:
        logger.error(f"Failed to clone {repo_url}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        repo = Repo('.')
        origin_url = repo.remotes.origin.url
    except InvalidGitRepositoryError:
        logger.error("Current directory is not a Git repository")
        sys.exit(1)
    except AttributeError:
        logger.error("No origin remote found")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error determining repo base URL: {e}")
        sys.exit(1)

    repo_base = origin_url.rsplit("/", 1)[0] + "/"
    logger.info(f"Repo base URL: {repo_base}")

    all_repos = ["opencda", "artery"]
    repos = sys.argv[1:] if len(sys.argv) > 1 else all_repos
    logger.info(f"Repositories to process: {repos}")

    for repo in repos:
        tag = CAVISE_TAGS.get(repo)
        clone_repo(repo_base, repo, tag)

    logger.info("Operation completed successfully")
