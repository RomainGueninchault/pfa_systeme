"""Repository import and update module.

Manages importing new exercise repositories and pulling updates from remote
repositories with git integration.
"""
from ls import rebuild_index
import subprocess
import shutil
import sys
from pathlib import Path

RESET   = "\033[0m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"


def _run_git(args, cwd=None):
    """Execute a git command.
    
    Args:
        args: List of git command arguments.
        cwd: Working directory for the command.
        
    Returns:
        tuple: (success, stdout, stderr)
    """
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd) if cwd is not None else None,
            check=True,
            text=True,
            capture_output=True,
        )
        return True, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        stdout = (e.stdout or "").strip()
        stderr = (e.stderr or "").strip()
        return False, stdout, stderr


def _is_git_repo(path):
    """Check if a directory is a git repository.
    
    Args:
        path: Directory path to check.
        
    Returns:
        bool: True if it's a git repository, False otherwise.
    """
    ok, out, _ = _run_git(["rev-parse", "--is-inside-work-tree"], cwd=path)
    return ok and out == "true"


def _has_local_changes(path):
    """Check if a repository has local changes.
    
    Args:
        path: Repository path.
        
    Returns:
        bool: True if there are uncommitted changes, False otherwise.
    """
    ok, out, _ = _run_git(["status", "--porcelain"], cwd=path)
    if not ok:
        return True
    return bool(out)


def _current_branch(path):
    """Get the current git branch name.
    
    Args:
        path: Repository path.
        
    Returns:
        str or None: Branch name, or None if detached HEAD.
    """
    ok, out, _ = _run_git(["symbolic-ref", "--short", "HEAD"], cwd=path)
    return out if ok else None


def _ensure_upstream(path, branch):
    """Ensure upstream branch is configured.
    
    Args:
        path: Repository path.
        branch: Branch name.
        
    Returns:
        str or None: Upstream branch reference, or None on error.
    """
    ok, out, _ = _run_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd=path)
    if ok and out:
        return out

    ok_remote, _, _ = _run_git(["show-ref", "--verify", f"refs/remotes/origin/{branch}"], cwd=path)
    if not ok_remote:
        return None

    ok_set, out_set, err_set = _run_git(
        ["branch", "--set-upstream-to", f"origin/{branch}", branch], cwd=path
    )
    if not ok_set:
        detail = err_set or out_set or "unknown error"
        print(f"{RED}[{path.name}] Cannot set upstream: {detail}{RESET}")
        return None

    return f"origin/{branch}"


def _pull_one_repo(repo_path):
    """Pull updates from a single repository.
    
    Args:
        repo_path: Path to the repository.
        
    Returns:
        str: Status of the pull operation (updated, unchanged, skipped, failed).
    """
    name = repo_path.name

    if not repo_path.is_dir():
        print(f"{YELLOW}[{name}] skipped: not a directory{RESET}")
        return "skipped"

    if not _is_git_repo(repo_path):
        print(f"{YELLOW}[{name}] skipped: not a git repository{RESET}")
        return "skipped"

    ok_remote, _, err_remote = _run_git(["remote", "get-url", "origin"], cwd=repo_path)
    if not ok_remote:
        detail = err_remote or "remote 'origin' missing"
        print(f"{RED}[{name}] error: {detail}{RESET}")
        return "failed"

    if _has_local_changes(repo_path):
        print(f"{YELLOW}[{name}] skipped: local changes detected{RESET}")
        return "skipped"

    branch = _current_branch(repo_path)
    if not branch:
        print(f"{RED}[{name}] error: detached HEAD{RESET}")
        return "failed"

    ok_fetch, out_fetch, err_fetch = _run_git(["fetch", "--prune", "origin"], cwd=repo_path)
    if not ok_fetch:
        detail = err_fetch or out_fetch or "fetch failed"
        print(f"{RED}[{name}] error: {detail}{RESET}")
        return "failed"

    upstream = _ensure_upstream(repo_path, branch)
    if not upstream:
        print(f"{YELLOW}[{name}] skipped: no upstream for '{branch}'{RESET}")
        return "skipped"

    ok_local, local_sha, _ = _run_git(["rev-parse", "HEAD"], cwd=repo_path)
    ok_upstream, upstream_sha, _ = _run_git(["rev-parse", upstream], cwd=repo_path)
    ok_base, base_sha, _ = _run_git(["merge-base", "HEAD", upstream], cwd=repo_path)

    if not (ok_local and ok_upstream and ok_base):
        print(f"{RED}[{name}] error: cannot compute state{RESET}")
        return "failed"

    if local_sha == upstream_sha:
        print(f"{BLUE}[{name}] already up to date{RESET}")
        return "unchanged"

    if local_sha != base_sha and upstream_sha != base_sha:
        print(f"{YELLOW}[{name}] skipped: diverged branch{RESET}")
        return "skipped"

    if upstream_sha == base_sha:
        print(f"{YELLOW}[{name}] skipped: local ahead{RESET}")
        return "skipped"

    ok_pull, out_pull, err_pull = _run_git(["pull", "--ff-only"], cwd=repo_path)
    if not ok_pull:
        detail = err_pull or out_pull or "pull failed"
        print(f"{RED}[{name}] error: {detail}{RESET}")
        return "failed"

    print(f"{BLUE}[{name}] updated successfully{RESET}")
    return "updated"


def pullRun(args):
    """Pull updates for exercise repositories.
    
    Args:
        args: Command-line arguments containing base_dir and optional repo filter.
        
    Returns:
        bool: True if all pulls succeeded, False if any failed.
    """
    if shutil.which("git") is None:
        print(f"{RED}git doesn't exist{RESET}")
        return False

    base_dir = Path(args.base_dir).expanduser()
    if not base_dir.exists() or not base_dir.is_dir():
        print(f"{RED}Base directory not found: {base_dir}{RESET}")
        return False

    repo_name = getattr(args, "repo", None)
    targets = [base_dir / repo_name] if repo_name else [p for p in sorted(base_dir.iterdir()) if p.is_dir()]

    if not targets:
        print(f"{YELLOW}No repository found{RESET}")
        return False

    stats = {"updated": 0, "unchanged": 0, "skipped": 0, "failed": 0}

    for repo_path in targets:
        status = _pull_one_repo(repo_path)
        if status in stats:
            stats[status] += 1

    if stats["updated"] > 0:
        rebuild_index(str(base_dir))

    print(
        f"{BLUE}Summary:{RESET} "
        f"{BLUE}updated={stats['updated']}{RESET} "
        f"{BLUE}unchanged={stats['unchanged']}{RESET} "
        f"{YELLOW}skipped={stats['skipped']}{RESET} "
        f"{RED}failed={stats['failed']}{RESET}"
    )

    return stats["failed"] == 0


def importRun(args):
    """Import a new exercise repository.
    
    Args:
        args: Command-line arguments containing the URL and base_dir.
    """
    if shutil.which("git") is None:
        print(f"{RED}git doesn't exist{RESET}")
        sys.exit(1)

    base_dir = Path(args.base_dir).expanduser()
    base_dir.mkdir(parents=True, exist_ok=True)

    name = args.url.split("/")[-1].removesuffix(".git")
    dest = base_dir / name

    if dest.exists():
        print(f"{YELLOW}Already installed{RESET}")
        return

    try:
        subprocess.run(["git", "clone", args.url, str(dest)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"{RED}Clone failed (code={e.returncode}){RESET}")
        return

    rebuild_index(args.base_dir)
    print(f"{BLUE}Repository installed successfully{RESET}")