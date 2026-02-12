#!/usr/bin/env python3

import os
import re
import sys
import argparse
import logging
from typing import List, Literal, Tuple

from git import Repo, cmd
from git.exc import GitCommandError, InvalidGitRepositoryError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
ALLOWED_REPOS = {"opencda", "artery"}


def get_available_versions(repo_url: str) -> List[Tuple[Literal["tag", "branch"], str]]:
    """
    Retrieves all available branches and tags from a remote Git repository.

    Runs `git ls-remote` against the given URL to fetch refs for both heads
    (branches) and tags. Parses the output with regex to extract ref names
    and returns a list of tuples: ("tag", name) or ("branch", name). Does not
    clone the repo; only queries the remote. Raises GitCommandError if the
    remote is unreachable or the URL is invalid.
    """
    logger.info("Getting repo versions: %s...", repo_url)
    try:
        git = cmd.Git()
        refs_output = git.ls_remote("--heads", "--tags", repo_url).strip()

        versions: List[Tuple[Literal["tag", "branch"], str]] = []
        tag_pattern = r"refs/tags/(.+?)$"
        for match in re.finditer(tag_pattern, refs_output, re.MULTILINE):
            tag_name: str = match.group(1)
            versions.append(("tag", tag_name))

        branch_pattern = r"refs/heads/(.+?)$"
        for match in re.finditer(branch_pattern, refs_output, re.MULTILINE):
            branch_name: str = match.group(1)
            versions.append(("branch", branch_name))

        return versions
    except GitCommandError:
        logger.exception("Failed to get available versions for %s", repo_url)
        sys.exit(1)


def select_version_interactive(repo_name: str, repo_url: str) -> str:
    """
    Lets the user pick a branch or tag interactively from the given repository.

    Fetches available versions via get_available_versions, logs a numbered
    list (tags and branches), then prompts the user to enter a number. Loops
    until a valid choice is made. Returns the selected ref name (e.g. "main"
    or "v0.1.0"). Raises ValueError if no versions are available.
    """
    versions = get_available_versions(repo_url)

    if not versions:
        raise ValueError("Cannot get repo versions. Please check your local repository or try to clone it again.")
    text = f"{repo_name} versions:"
    for i, (ref_type, version) in enumerate(versions, 1):
        text += f"\n{i}. [{ref_type}] {version}"
    logger.info(text)

    while True:
        try:
            choice = input(f"Choose version: (1-{len(versions)}): ").strip()
            choice_num = int(choice)
            if 1 <= choice_num <= len(versions):
                selected = versions[choice_num - 1][-1]
                break
            else:
                logger.warning("Choose from 1 to %s", len(versions))
        except ValueError:
            logger.warning("Wrong value, try one more time")
    return selected


def clone_repo(repo_base: str, repo_name: str, version: str) -> None:
    """
    Clones a Git repository into a directory named after the repo.

    Builds the full URL as repo_base + repo_name. If a directory with that
    name already exists, logs a message and returns without cloning. Otherwise
    clones with submodules (recursive=True). If version is given, checks out
    that branch or tag; otherwise uses the default branch. On clone failure,
    logs the error and exits the process with code 1.
    """
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
    except GitCommandError:
        logger.exception("Failed to clone %s", repo_url)
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    """
    Parses command-line arguments for the setup script.

    Defines optional version flags for opencda and artery (-o/--opencda-version,
    -a/--artery-version) and optional positional arguments for which repos to
    clone (opencda, artery, or both). Returns the parsed namespace from
    argparse.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--opencda-version",
        type=str,
        help="Version (branch or tag) for opencda. Default: main",
    )
    parser.add_argument(
        "-a",
        "--artery-version",
        type=str,
        help="Version (branch or tag) for artery. Default: main",
    )
    parser.add_argument(
        "repos",
        nargs="*",
        help="Repos for cloning (`opencda`, `artery`). Default: all",
    )

    args = parser.parse_args()

    # Some IDE task runners pass an empty list literal (`[]`) as a positional arg.
    # Treat it as "no repos provided" to keep CLI behavior simple.
    cleaned_repos = [repo.strip() for repo in args.repos if repo.strip() and repo.strip() != "[]"]
    invalid_repos = [repo for repo in cleaned_repos if repo not in ALLOWED_REPOS]
    if invalid_repos:
        parser.error(f"argument repos: invalid choice(s): {invalid_repos} (choose from {', '.join(sorted(ALLOWED_REPOS))})")
    args.repos = cleaned_repos

    return args


def main() -> None:
    """
    Entry point: clones opencda and/or artery using versions from CLI or prompts.

    Resolves the base URL from the current repo's origin remote. Determines
    which repos to process (default: both). For each repo, uses the version
    from the corresponding CLI flag if set; otherwise runs
    select_version_interactive to ask the user. Then calls clone_repo for each.
    Exits with code 1 if not in a Git repo, if origin is missing, or if clone
    fails.
    """
    args = parse_args()

    try:
        repo = Repo(".")
        origin_url = repo.remotes.origin.url
        repo_base = origin_url.rsplit("/", 1)[0] + "/"
        raise InvalidGitRepositoryError
    except InvalidGitRepositoryError:
        logger.exception("Current directory is not a Git repository")
        sys.exit(1)
    except AttributeError:
        logger.exception("No origin remote found")
        sys.exit(1)
    except Exception:
        logger.exception("Error determining repo base URL")
        sys.exit(1)

    repos = args.repos if args.repos else ["opencda", "artery"]
    logger.info(f"Repositories to process: {repos}")

    for repo_name in repos:
        match repo_name:
            case "opencda":
                version = args.opencda_version
            case "artery":
                version = args.artery_version
            case _:
                version = None

        if version is None:
            repo_url = f"{repo_base}{repo_name}"
            version = select_version_interactive(repo_name, repo_url)

        clone_repo(repo_base, repo_name, version)

    logger.info("Operation completed successfully")


if __name__ == "__main__":
    main()
