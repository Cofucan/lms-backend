
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

Please ensure code is properly tested.

1. Fork the Project repo

2. Clone the repo to your local machine using 

`git clone https://github.com/<your-account-name>/project-lms-backend`
3. Set your Upstream Remote using 

`git remote add upstream https://github.com/kodecampteam/project-lms-backend`
4. Create your Feature Branch using 

`git checkout -b <name-of-feature>`

(Tip: the name of your branch should be closely related to the feature being worked on and make sure to always create new feature branch from the dev branch and not master. Ensure your local dev branch is up to date with upstream remote dev branch before creating new branch.)

5. Set up your development environment (Tip: see ##Getting Started guide below)

6. Make and commit your changes (Use a concise descriptive commit message)

7. Pull latest updates from Upstream branch using 

`git pull upstream dev`
8. If conflicts are encountered after pulling changes, please resolve them locally first before committing

9. Push your Feature Branch to origin using 

`git push origin <name-of-your-feature-branch>`

10. Go to Github, open a Pull Request to the dev branch and request a review by tagging team members 


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
