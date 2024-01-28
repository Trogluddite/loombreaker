# Git/Github tips/tricks (*nix quickstart)
These are the processes Joe follows, and they should work for *nix OS's (Linux, MacOS terminal)
If you already have a preferred method for interacting with Github or Git repos, you can skip this!

## Optional, but preferred: set up SSH for github
Setting up an SSH keypair allows you to use git commands without entering a password
### follow instructions for your platform to set up a keypair:
https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
### Add your public key to Github:
https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account

## Repo actions
### Clone the repo
```
% git clone git@github.com:Trogluddite/loombreaker.git
% cd loombreaker
```
### list your local branches (default is 'main')
```
% git branch --list
```
### create a new branch
Pushing to the default branch is disabled in this project, so you'll need to make a branch or a fork repo (I'm not covering forks right now)
```
% git pull # recommended; make sure your main branch is up to date before you branch off of it
% git branch myBranch
% git checkouyt myBranch
```
make some changes
### Add your changes, commit, make a pull request
```
% git status #show staged/unstaged files
% git add -A #stage ALL unstaged files (staging means "include in the next commit")
% git add someFileName # stage one file for the next commit
% git commit -m "some description of the commit"  # commit the change; -m means message. 
% git push --set-upstream origin myBranch  # pushes your modifications into a branch, upstream
```
At this point your changes are on the upstream repo, and ready for review and a pull request. 
Follow this guide to create a pull request (or, Joe is glad to help)
https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request 

you can make changes to your Pull Request until it's merged; follow the process above to add changes and push. On your second push, you won't need to use --set-upstream

after your pull request is merged, I like to discard the branch and start fresh. It reduces merging & rebasing.
### Update main and prepare for another change
After I'm done with a branch (I.E., I'm done with a discrete change I intended to make), I do this:
```
% git checkout main
% git pull
% git branch -d myBranch
% git branch newBranch
% git checkout newBranch
```
I find it much easier to just discard branches, and only pull downstream to my 'main' branch; there's a lot less confusion about merges and history.
### Look at change log: 
```
% git log
% git log --graph  # useful for workflows that use merge; Joe prefers rebasing for a linear history
```
### Additional!
Let's add to this over time, if needed; Git is really powerful and worth learning beyond a basic workflow like the above.
