# Goals

- Search for Python packages
- Order package list by relevance for the user:
  - popularity (to be defined)
- Reasonable filtering:
  - only show packages you would actually use (no alpha software,
    no libraries when looking for apps, no abandoned projects)
- Incorporate data from other sources (GitHub starts, issues, commits,
  trends, ...)

# Development setup

Run `poetry shell` and `poetry install`.

## PostgreSQL

Create a directory for Postgres data and start a Postgres Docker container:

```bash
mkdir postgres-data
docker run --rm --name petshop-postgres -e POSTGRES_PASSWORD=password -p 127.0.0.1:5439:5432 -d -v $PWD/postgresql-data/:/var/lib/postgresql/data postgres:14
```

## Login to Google services

Install the `gcloud` command line utility.

Login to Google Cloud Console and create a new project, let’s call
it `petshop`. It will be assigned a name like `petshop-<some numbers>`.
This is the project name.

Enable the "Cloud Resource Manager API" via Menu→API&Services→Enabled APIs&services, then search for `cloudresourcemanager`.

Create a `.env` file with content `GOOGLE_CLOUD_PROJECT=<project-name>`.
