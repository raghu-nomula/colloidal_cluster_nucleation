# Git and GitHub: owner's cheat-sheet

Written for someone who is new to git. Nothing here needs to be memorised; copy the commands.

## Ideas in five lines

* A **repository (repo)** is the project folder plus its complete history of changes.
* A **commit** is a saved snapshot with a message (like "save as", but remembered forever).
* A **branch** is a separate line of work. `main` is the official version. Changes happen on other branches.
* A **pull request (PR)** is a proposal: "please merge my branch into `main`". The owner reads it and decides.
* A **fork** is a collaborator's own copy of the repo on GitHub, from which they send pull requests. Because they
  only have a fork, only the owner can change `main`.

## Everyday commands (on your own computer, inside the repo folder)

| I want to… | Command |
|---|---|
| see what changed | `git status` |
| see the details of the change | `git diff` |
| save my changes | `git add <file>` then `git commit -m "short clear message"` |
| see history | `git log --oneline` |
| get the latest from GitHub | `git pull` |
| send my commits to GitHub | `git push` |
| undo a change in a file I have not committed | `git restore <file>` (this throws the change away) |

Rules of thumb: commit small and often; write messages that say *what and why*; never use `git add .` without
reading `git status` first; never add trajectories or passwords (`.gitignore` helps but check).

## Reviewing a collaborator's pull request (on github.com)

1. Open the repo → tab **Pull requests** → click the request.
2. Tab **Files changed**: read the changes. Click the `+` next to a line to comment on it.
3. Check the checklist in the description (no big files, relative paths, cluster definition stated).
4. Click **Review changes** and choose *Comment*, *Request changes* or *Approve*.
5. When you are satisfied: **Merge pull request** (button at the bottom). The change is now in `main`.
6. Mistake after merging? Use **Revert** on the merged pull request page; it creates a new pull request that undoes it.

## If something goes wrong

* *"I committed a big file."* Do **not** push. Tell your assistant or run `git reset --soft HEAD~1`, unstage the
  file, and commit again. (Once pushed, a big file stays in the history; that is why we check before pushing.)
* *"I pushed something private."* Tell your assistant immediately; the history may need rewriting.
* *"I deleted a file by mistake."* If it was committed, `git restore <file>` brings it back.

## Before the repo is ever made public

Check the licence of the code that came from the Frenkel–Smit book, choose a licence, remove anything not
allowed, and read the whole history for files that should not be public. Private → public is a one-way decision
for anything already cloned.
