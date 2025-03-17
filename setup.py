#!/usr/bin/env python3

import os
import sys
import logging
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def clone_repo(repo_base, repo_name):
    repo_url = f"{repo_base}{repo_name}"
    if os.path.isdir(repo_name):
        logger.info(f"Repository {repo_name} already exists. Skipping.")
        return
    
    logger.info(f"Cloning {repo_url}...")
    try:
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

    # Формируем базовый URL
    repo_base = origin_url.rsplit("/", 1)[0] + "/"
    logger.info(f"Repo base URL: {repo_base}")

    # Список репозиториев для клонирования
    all_repos = ["opencda", "artery", "scenario-manager"]
    repos = sys.argv[1:] if len(sys.argv) > 1 else all_repos
    logger.info(f"Repositories to process: {repos}")

    # Клонируем каждый репозиторий
    for repo in repos:
        clone_repo(repo_base, repo)

    logger.info("Operation completed successfully")