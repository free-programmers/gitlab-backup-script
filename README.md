# GitLab Group & Project Backup Script

This Python script mirrors all GitLab groups, subgroups, and projects
you have access to into a local directory, preserving the exact GitLab
hierarchy.

## What This Script Does

-   Fetches all **top-level GitLab groups** you have access to

-   Automatically includes all **subgroups (recursive)**

-   Clones every project into a local folder structure that matches
    GitLab:

        group/
          ├── project
          └── subgroup/
              └── project

-   If a repository already exists locally, it performs a `git pull`
    instead of re-cloning

## Use Case

Ideal for: - Creating local backups of GitLab repositories - Migrating
or mirroring GitLab projects - Offline access to all group-based
repositories - Keeping a local copy synchronized with GitLab

## Requirements

-   Python 3.7+
-   `git` installed and available in PATH
-   A GitLab **Personal Access Token** with repository access

## Configuration

Edit the following variables in the script:

``` python
ACCESS_TOKEN = "your_gitlab_access_token"
GITLAB_INSTANCE = "https://your.gitlab.instance"
```

## How It Works (High Level)

1.  Retrieves all root-level GitLab groups
2.  Requests all projects in each group (including subgroups)
3.  Builds folders based on `path_with_namespace`
4.  Clones or updates repositories accordingly

## Notes

-   Uses GitLab REST API v4
-   Preserves GitLab folder structure exactly
-   Works with self-hosted GitLab instances

## License


