
<!-- ABOUT THE PROJECT -->
## About The Project

This repository represents the backend architecture of lms.



### Built With <a name = "built-with"></a>
The list of all the major technologies used in the project.
- [Docker](https://www.docker.com/)
- [FastAPI](https://fastapi.tiangolo.com)
- [Postgres](https://www.postgresql.org/)
- [Redis](https://redis.io/)



## Getting Started

NB: All commands above are shortcut. Navigate to [MakeFile](./MakeFile) to see list of all commands

<!-- CONTRIBUTING -->
## Contributing

Please ensure code is properly tested.

1. Fork the Project
2. Create your Feature Branch 
3. Commit your Changes.
4. Push to the Branch
5. Open a Pull Request


## Getting Started
1. Clone the repository.
2. Create a `.env` file at the project root.
3. Populate your `.env` with the following:

```python
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_SERVER=db
    POSTGRES_PORT=5432
    POSTGRES_DB=postgres
    SECRET_KEY=bvpQJopvXGNJw6wCIYjvcBJZfm37W7sKSUc9kTw0PKIixQNr9B
    ALGORITHM=HS256
```
4. Run `make build` to build the containers.
5. Run `make up` to start the containers.
6. Run `make test` to execute unit/integration tests.
