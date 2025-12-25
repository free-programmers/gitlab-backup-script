import requests
import os
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from typing import List, Dict, Optional

# ================== CONFIG ==================
GITLAB_INSTANCE = "https://gitlab.com"
BASE_PATH = os.path.join(os.getcwd(), "repos")

ACCESS_TOKEN = os.getenv("GITLAB_TOKEN", "glpat-XXXX")  # Prefer env var

REQUEST_TIMEOUT = 15
PER_PAGE = 100

# ================== LOGGING ==================
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("gitlab_backup")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

# Console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# File (rotating)
file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "backup.log"),
    maxBytes=2_000_000,
    backupCount=3
)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# ================== HTTP ==================
HEADERS = {
    "PRIVATE-TOKEN": ACCESS_TOKEN
}

session = requests.Session()
session.headers.update(HEADERS)

# ================== FUNCTIONS ==================
def gitlab_get(url: str, params: Optional[Dict] = None) -> List[Dict]:
    """Paginated GET request to GitLab API"""
    results = []
    page = 1

    while True:
        query = params.copy() if params else {}
        query.update({"page": page, "per_page": PER_PAGE})

        try:
            response = session.get(url, params=query, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"GitLab API error: {e}")
            break

        data = response.json()
        if not data:
            break

        results.extend(data)
        page += 1

    return results


def clone_or_pull(repo_url: str, path: str) -> None:
    """Clone repo if missing, otherwise pull"""
    try:
        if not os.path.exists(path):
            logger.info(f"Cloning: {path}")
            subprocess.run(
                ["git", "clone", repo_url, path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
        else:
            logger.info(f"Pulling: {path}")
            subprocess.run(
                ["git", "-C", path, "pull"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
    except subprocess.CalledProcessError as e:
        logger.error(f"Git error on {path}: {e.stderr.decode().strip()}")


# ================== MAIN ==================
def main():
    os.makedirs(BASE_PATH, exist_ok=True)

    logger.info("Starting GitLab backup")

    groups = gitlab_get(
        f"{GITLAB_INSTANCE}/api/v4/groups",
        {"min_access_level": 10, "top_level_only": True}
    )

    logger.info(f"Found {len(groups)} root groups")

    for group in groups:
        logger.info(f"Processing group: {group['full_path']}")

        projects = gitlab_get(
            f"{GITLAB_INSTANCE}/api/v4/groups/{group['id']}/projects",
            {"include_subgroups": True}
        )

        logger.info(f"  Projects found: {len(projects)}")

        for project in projects:
            project_dir = os.path.join(
                BASE_PATH,
                project["path_with_namespace"]
            )
            os.makedirs(os.path.dirname(project_dir), exist_ok=True)

            clone_or_pull(project["http_url_to_repo"], project_dir)

    logger.info("GitLab backup completed successfully")


if __name__ == "__main__":
    main()
