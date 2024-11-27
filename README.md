# RAG-API Application Skeleton: A starter kit for building production RAG applications

Looking to build and deploy a real-world RAG application? Welcome!

This repo provides a base skeleton for building a [(RAG)](https://en.wikipedia.org/wiki/Retrieval-augmented_generation)-enhanced LLM application. It is intended to serve as a starting point for developers looking to build real-world production RAG applications.

This allows easy setup of a web application that allows you to input large amounts of custom data for use with your LLM, operated via a web API.

## What's Included

The project allows you to:
1. Locally deploy (via Docker) a vector database.
1. Locally deploy an API to add/remove custom textual data from the vector DB.
1. Instructions on how to deploy to AWS.
1. An API to send chat messages to the LLM, which can be used to ask questions about the custom data. It can "look up" data from the vector DB for use as part of the response.
1. Chat history is stored in a local Postgres, and is also accesable via the API.
1. The API supports streaming of the response from the LLM.

This repo is built by Hipposys Ltd., and serves as a starting off point for new RAG projects for our clients. It is open sourced both for educational purposes, and to serve as a base for commercial projects.

The current skeleton supports Amazon Bedrock or OpenAI as the LLM provider, and Milvus or Chroma as the vector database. Additional LLM providers and vector databases are planned to be added in the near future.

## Features

- Web Server providing endpoints for:
    -  Adding and removing custom data.
    - Sending and receiving chat messages.
        - This supports streaming of the response from the LLM.
- Using Amazon Bedrock or OpenAI as an LLM provider.
- Milvus and Chroma Vector database integrations.
- Built on top of Langchain.
- Chat history is stored in a local Postgres, and is also accesable via the API.

## Prerequisites

Currently, you must have an Amazon Bedrock or OpenAI account to use this project.

You'll also need Docker for the local deploy.

## Contact

Looking for help or have questions? Contact us at [contact@hipposys.com](mailto:contact@hipposys.com).

We work with clients on a variety of AI engineering and Data Enngineering projects.

## Installation

The local deployment relies on having Docker installed.

It also relies on having access to Amazon Bedrock or OpenAI models, which are used as the LLM provider of the application.

### Local Deployment

1. Clone the repository:
    ```bash
    git clone https://github.com/hipposys-ltd/rag-app-skeleton.git
    ```
1. Navigate to the project directory:
    ```bash
    cd rag-app-skeleton
    ```
1. Make sure you have Docker installed and running.
1. Create an `.env` file:
    1. `cp .env-template .env`
    1. Fill it in with the necessary credentials and settings.
    1. For the initial local deplyment, the most important credentials are the ones defining your LLM provider:
        1. `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` if you'll be using `AWS`.
        1. `OPENAI_API_KEY` if you'll be using OpenAI.
        1. Other credentials may be suitable for local development, but should be replaced when deploying to a remote server (e.g. `prod`) for additional security.
1. Build and run the project via Docker: `docker compose -f docker-compose.yml -f docker-compose.milvus.yml up -d --build`
1. After running docker, you should have multiple services running.
    1. You can check the status of the services with `docker ps -a`.
    1. Make sure the `fastapi`, `postgres` and `milvus-standalone` containers are running.
1. Go to `localhost:8080/hello-world` to see an `{"hello": "world"}` response from the server.
1. You now have a running instance of the RAG application.


### Setting Up Bedrock

1. Make sure that you have a Bedrock model available in your AWS account:
    1. Log into the AWS console.
    1. Navigate to the `Amazon Bedrock` service.
    1. In the left navigration pane: `Bedrock configurations` -> `Model access`.
    1. We currently use `Claude 3.5 Sonnet` for inference and `Titan Text Embeddings V2` for embeddings.
        1. Note that this may change, you can either change it yourself, or see that someone else has changed it in the code.
        1. Note that these models may not be available in all regions, we currently use `us-east-1` (N. Virginia).
    1. If these models are not enabled, you'll have to ask for access. The access should be granted immediately upon request.
    1. You'll need to generate access credentials for your Amazon account for use in the application.

### Setting Up OpenAI

1. In your `.env` file:
    1. Add your [`OPENAI_API_KEY`](https://platform.openai.com/api-keys).
    1. Set the `LLM_MODEL_ID` to an OpenAI-compatible model (e.g., `gpt-3.5-turbo`).
    1. Comment out any unused environment variables (e.g., AWS-related variables).
1. In `app/models/__init__.py`, update the code to use OpenAI models instead of the default Bedrock models. Make sure to adjust both the model for inference and the one for embeddings.
1. Finally, restart Docker Compose to apply the `.env` changes.

## Example Usage

We're now going to give a simple example of how to use the API. The plan is to:

1. Query our LLM, via the API, and ask for specific "inside" information, which it does not have access to.
1. Use the API to add the information to the vector database via simple textual data.
1. Query the LLM again and ask for the same information, which it now has access to.

Note that by default, the repo is configured to return simple textual responses when running in `local` mode (controlled via `.env`) and JSON-formatted responses when running in non `local` modes (e.g. `prod`).


### 1. Query the LLM via the API

The following command sends a chat query via the API.:

```bash
curl \
    -i \
    -X POST \
    --no-buffer \
    -b cookies.tmp.txt -c cookies.tmp.txt \
    -H 'Content-Type: application/json' \
    -d '{"message": "What headphones are recommended by the company for listening to podcasts?"}' \
    http://localhost:8080/chat/ask
```

Highlighting the important things in the command:
- We are hitting the `/chat/ask` endpoint to actually ask the LLM a question.
- We are using `-b` and `-c` to save the cookies from the server. This lets the server continue our chat session, so additional requests to `/chat/ask` will be part of the same chat session.
- The message itself is the chat message we are sending to the LLM.

The output should be a message of not finding anything in the company's internal documents about a headphone recommendation. There will also likely be a general message trying to help.

### 2. Add information to the vector database

We'll add two sources of information to the vector database about Heapdhone choices:

```bash
curl \
    -i \
    -X POST \
    --no-buffer \
    -b cookies.tmp.uc.txt -c cookies.tmp.uc.txt \
    -H 'Content-Type: application/json' \
    -d '{"source_id": "1001", "source_name": "Headphones Guide I", "text": "The recommended headphones to use while listening to podcasts are AirPods Pro", "modified_at": "2024-09-22T17:04"}' \
    http://localhost:8080/embeddings/text/store
```

```bash

curl \
    -i \
    -X POST \
    --no-buffer \
    -b cookies.tmp.uc.txt -c cookies.tmp.uc.txt \
    -H 'Content-Type: application/json' \
    -d '{"source_id": "1001", "source_name": "Headphones Guide II", "text": "The recommended headphones to use while listening to music is BoseQC35", "modified_at": "2024-09-22T17:04"}' \
    http://localhost:8080/embeddings/text/store
```


Here, we are sending data to the `/embeddings/text/store` endpoint. This endpoint is responsible for storing the text data in the vector database. We store the data itself, as well as metadata about the source of the data - the source name, the source id, and the modification date.


### 3. Query the LLM again

Now we can query the LLM again and ask for the same information, which it now has access to:

```bash
curl \
    -i \
    -X POST \
    --no-buffer \
    -b cookies.tmp.txt -c cookies.tmp.txt \
    -H 'Content-Type: application/json' \
    -d '{"message": "What headphones are recommended by the company?"}' \
    http://localhost:8080/chat/ask
```

This time, you shold see a response from the LLM that includes the information we added to the vector database.

### Other API Endpoints

You can delete a source using the `/embeddings/text/delete` endpoint:
```bash
curl \
    -i \
    -X DELETE \
    --no-buffer \
    -b cookies.tmp.txt -c cookies.tmp.txt \
    -H 'Content-Type: application/json' \
    -d '{"source_id": "1001"}' \
    http://localhost:8080/embeddings/text/delete
```

## Other Configuration

### Using a Different Vector DB

Currently, the project supports Chroma and Milvus, with plans to add more vector databases in the future. By default, Milvus is used, but switching to another supported database is simple:

1. Open `app/databases/vector/__init__.py` and update the `VectorDB` assignment. For example, to switch to Chroma:
    ```python
    from app.databases.vector.chroma import Chroma
    # from app.databases.vector.milvus import Milvus

    VectorDB = Chroma
    ```
1. When running `docker compose`, use the `docker-compose` configuration file that matches the database you’ve chosen. For example, to use `Chroma`:
    ```bash
    docker compose \
        -f docker-compose.yml \
        -f docker-compose.chromadb.yml \
        up -d --build
    ```

## Testing

To run the tests, use the following command:

```bash
docker exec -it fastapi bash -c "pytest app/"
```

For faster test execution, at the expense of cleaner output, you can add the `-n` option to parallelize tests across multiple workers:

```bash
docker exec -it fastapi bash -c "pytest -n 5 app/"
```

In this example, 5 parallel workers will execute the tests.

## Deploying to Production

A more complete guide to deploying to production will be added later.

For now, you can check the notes in `prod/README.md` and the other files in that directory.

## Running Jupyter Notebook

When starting the project locally (following the instructions above), a Jupyter Lab server will automatically start. The server configuration is defined in `docker-compose.yml`.

To access Jupyter Lab, open http://localhost:8890 in your web browser. On your first visit, you’ll need to provide a login token. You can retrieve the token from the logs of the `jupyter` Docker container by running:

```bash
docker logs jupyter 2>&1 | grep token= | tail -n 1 | grep -E '=.+$'
```

After logging in, navigate to `/work/notebooks` to access the existing notebooks or create new ones.
