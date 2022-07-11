
<!-- ABOUT THE PROJECT -->
## About The Project

This repository represents the backend architecture of KodeCamp Learning Management System (LMS).



### Built With <a name = "built-with"></a>
The list of all the major technologies used in the project.
- [Docker](https://www.docker.com/)
- [FastAPI](https://fastapi.tiangolo.com)
- [Postgres](https://www.postgresql.org/)
- [Redis](https://redis.io/)



<!-- CONTRIBUTING -->
## Contribution Guide

Please ensure your codes and changes are properly tested.


### Fork the Project Repo

Fork this repository to get a personal copy on your github account


### Clone the Repo to your local machine using

To clone the forked repository to your local machine, open command prompt and run:

`git clone https://github.com/<your-account-name>/project-lms-backend`


### Set Upstream Remote

Set your upstream remote so you can pull changes from upstream to update your repo by running:

`git remote add upstream https://github.com/kodecampteam/project-lms-backend`


### Creating Feature Branch

First checkout to the dev branch by running:

`git checkout dev`

Then create the feature branch by running:

`git checkout -b <name-of-feature>`

NB: the name of your branch should be closely related to the feature being worked on and make sure to always create new feature branch from the dev branch and not master. Ensure your local dev branch is up to date with upstream remote dev branch before creating new branch.


### Set up Development Environment 

Tip: see Getting Started guide below


### Making Changes

Make all your changes on your feature branch, add and commit your changes using a concise descriptive commit message


### Pulling Updates from Remote

Pull latest updates from Upstream branch by running:

`git pull upstream dev`

NB: If conflicts are encountered after pulling changes, please resolve them locally first before committing


### Pushing Changes

Publish your Feature Branch and changes to origin by running:

`git push origin <name-of-your-feature-branch>`


### Pull Request

Go to Github, open a Pull Request to the Upstream Remote dev branch and request a review by tagging team members 


NB: Add a proper description of the changes made when making a Pull Request for easy review. Goodluck!!!


## Getting Started
1. Create a `.env` file at the project root.
2. Populate your `.env` with the following:

```python
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_SERVER=db
    POSTGRES_PORT=5432
    POSTGRES_DB=postgres
    SECRET_KEY=bvpQJopvXGNJw6wCIYjvcBJZfm37W7sKSUc9kTw0PKIixQNr9B
    ALGORITHM=HS256
```
3. Run `make build` to build the containers.
4. Run `make up` to start the containers.
5. Run `make test` to execute unit/integration tests.

NB: All commands above are shortcut. Navigate to [MakeFile](./MakeFile) to see list of all commands
