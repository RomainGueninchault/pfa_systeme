from ls import rebuild_index
import subprocess
import shutil
import sys
from pathlib import Path


def _run_git(args, cwd=None):
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
    ok, out, _ = _run_git(["rev-parse", "--is-inside-work-tree"], cwd=path)
    return ok and out == "true"


def _has_local_changes(path):
    ok, out, _ = _run_git(["status", "--porcelain"], cwd=path)
    if not ok:
        return True
    return bool(out)


def _current_branch(path):
    ok, out, _ = _run_git(["symbolic-ref", "--short", "HEAD"], cwd=path)
    if not ok:
        return None
    return out


def _ensure_upstream(path, branch):
    ok, out, _ = _run_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd=path)
    if ok and out:
        return out

    ok_remote, _, _ = _run_git(["show-ref", "--verify", f"refs/remotes/origin/{branch}"], cwd=path)
    if not ok_remote:
        return None

    ok_set, out_set, err_set = _run_git(["branch", "--set-upstream-to", f"origin/{branch}", branch], cwd=path)
    if not ok_set:
        detail = err_set or out_set or "unknown error"
        print(f"Cannot set upstream for '{path.name}': {detail}")
        return None

    return f"origin/{branch}"


def _pull_one_repo(repo_path):
    name = repo_path.name

    if not repo_path.is_dir():
        print(f"[{name}] skipped: not a directory")
        return "skipped"

    if not _is_git_repo(repo_path):
        print(f"[{name}] skipped: not a git repository")
        return "skipped"

    ok_remote, _, err_remote = _run_git(["remote", "get-url", "origin"], cwd=repo_path)
    if not ok_remote:
        detail = err_remote or "remote 'origin' missing"
        print(f"[{name}] skipped: {detail}")
        return "skipped"

    if _has_local_changes(repo_path):
        print(f"[{name}] skipped: local changes detected (commit/stash first)")
        return "skipped"

    branch = _current_branch(repo_path)
    if not branch:
        print(f"[{name}] skipped: detached HEAD")
        return "skipped"

    ok_fetch, out_fetch, err_fetch = _run_git(["fetch", "--prune", "origin"], cwd=repo_path)
    if not ok_fetch:
        detail = err_fetch or out_fetch or "fetch failed"
        print(f"[{name}] failed: {detail}")
        return "failed"

    upstream = _ensure_upstream(repo_path, branch)
    if not upstream:
        print(f"[{name}] skipped: no upstream for branch '{branch}'")
        return "skipped"

    ok_local, local_sha, _ = _run_git(["rev-parse", "HEAD"], cwd=repo_path)
    ok_upstream, upstream_sha, _ = _run_git(["rev-parse", upstream], cwd=repo_path)
    ok_base, base_sha, _ = _run_git(["merge-base", "HEAD", upstream], cwd=repo_path)
    if not (ok_local and ok_upstream and ok_base):
        print(f"[{name}] failed: unable to compute branch state")
        return "failed"

    if local_sha == upstream_sha:
        print(f"[{name}] already up to date")
        return "unchanged"

    if local_sha != base_sha and upstream_sha != base_sha:
        print(f"[{name}] skipped: branch diverged from upstream")
        return "skipped"

    if upstream_sha == base_sha:
        print(f"[{name}] skipped: local branch is ahead of upstream")
        return "skipped"

    ok_pull, out_pull, err_pull = _run_git(["pull", "--ff-only"], cwd=repo_path)
    if not ok_pull:
        detail = err_pull or out_pull or "pull failed"
        print(f"[{name}] failed: {detail}")
        return "failed"

    print(f"[{name}] updated successfully")
    return "updated"


def pullRun(args):
    if shutil.which("git") is None:
        print("git doesn't exist")
        return False

    base_dir = Path(args.base_dir).expanduser()
    if not base_dir.exists() or not base_dir.is_dir():
        print(f"Base directory not found: {base_dir}")
        return False

    repo_name = getattr(args, "repo", None)
    if repo_name:
        targets = [base_dir / repo_name]
    else:
        targets = [p for p in sorted(base_dir.iterdir()) if p.is_dir()]

    if not targets:
        print("No repository found to update")
        return False

    stats = {"updated": 0, "unchanged": 0, "skipped": 0, "failed": 0}
    for repo_path in targets:
        status = _pull_one_repo(repo_path)
        if status in stats:
            stats[status] += 1

    if stats["updated"] > 0:
        rebuild_index(str(base_dir))

    print(
        "Pull summary: "
        f"updated={stats['updated']} "
        f"unchanged={stats['unchanged']} "
        f"skipped={stats['skipped']} "
        f"failed={stats['failed']}"
    )

    return stats["failed"] == 0

def importRun(args):
    if shutil.which("git") is None:
        print("git doesn't exist")
        sys.exit(1)

    base_dir = Path(args.base_dir).expanduser()
    base_dir.mkdir(parents=True, exist_ok=True)

    name = args.url.split("/")[-1].removesuffix(".git")
    dest = base_dir / name

    if dest.exists():
        print("Already installed")
        return

    try:
        subprocess.run(["git", "clone", args.url, str(dest)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Clone failed (code={e.returncode})")

    # for bd    
    rebuild_index(args.base_dir)
    print("Repository installed successfully")

