## Conventions

##### Branching to make changes

Create a branch to make all updates on `git checkout -b <branch-name>` 

Try to make your branch name is descriptive of what your modifications are. 

Once you have completed your updates and **tested** them on the locally running dev site, you should create a pull request against the master branch. 

Assign someone else who is reasonably familiar with the goals of your updates (should be anyone for this project) to review your code. when you create the pull request (PR), there is a right sidebar where you can assign someone. Look at the diffs and review the code, test it. Once they have reviewed your code for good style and proper functionality they will comment on the PR that it is approved. Once it has been approved you may merge your branch to master. 


Making updates on branches and then merging them **after review & testing** will prevent you from getting into a situation where you accidentally commit something that breaks your main (master) branch and makes us all extremely stressed. 

##### Commits
Commits should be descriptive of their contents and the changes made.

##### Pull Requests
If making lots of updates to the site, create a separate branch and pull request for each distinct update. Pull requests should be as focused to a task/end goal as possible. 

If you need to update publications and some CSS, make a pull request for each. Try to to keep any given pull request focused on a single objective or update. 

## Pull Request Format
```
#### What/Why
What is this the the feature in this PR and why is it important.

#### Changes
Any changes to the system we should know about (got rid of x class in favor of y. Added tests, etc).

### Testing
Probably the most important part. Explain how to locally test your feature. IF there are any specific commands or things to stress-test include them here. 

#### Notes
Anything else. 
```

#### Helpful Git Commands
* `git fetch` update your list of branches in your local terminal
* `git branch` check which branch you are on
* `git stash` stash all changes made since the last commit
* `git reset` (has options, google) useful if you f*ck something up and want to go back to a pervious (working) commit
* `git checkout` switch between branches
* `git diff` see the changes you have made since your last commit
