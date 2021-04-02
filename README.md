# Pandas Accessors

Simple column selector for loc[], iloc[], assign and others.

# Development

Development is containerized with [Docker](https://www.docker.com/) to
separte from host systems and improve reproducability. No other
prerequisites are needed on the host system.

**Recommendation for Windows users:** install [WSL
2](https://docs.microsoft.com/en-us/windows/wsl/install-win10) (tested on
Ubuntu 20.04), and for containerized workflows, [Docker
Desktop](https://www.docker.com/products/docker-desktop) for Windows.

The **common tasks** are collected in `Makefile` (See `make help` for a
complete list):

- Run the unit tests: `make test` or `make watch` for continuously running
  tests on code-changes.
- Build the documentation: `make docs`
- **TODO**: Update the `poetry.lock` file: `make lock`
- Add a dependency:
  1. Start a shell in a new container.
  2. Add dependency with `poetry add` in the running container. This will update
     `poetry.lock` automatically.
  ```sh
  # 1. On the host system
  % make shell
  # 2. In the container instance:
  I have no name!@7d0e85b3a303:/app$ poetry add --dev --lock falcon
  ```
- Build the development image `make devimage`
  (Note: This should be done automatically for the targets.) 
