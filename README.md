# RAG-API Application Skeleton: A starter kit for building production RAG applications

Looking to build and deploy a real-world RAG application? Welcome!

This repo provides a base skeleton for building a [(RAG)](https://en.wikipedia.org/wiki/Retrieval-augmented_generation)-enhanced LLM application. It is intended to serve as a starting point for developers looking to build real-world production RAG applications.

This allows easy setup of a web application that allows you to input large amounts of custom data for use with your LLM, operated via a web API.

## What's included

The project allows you to:
1. Locally deploy (via Docker) a vector database.
1. Locally deploy an API to add/remove custom textual data from the vector DB.
1. An API to send chat messages to the LLM, which can be used to ask questions about the custom data. It can "look up" data from the vector DB for use as part of the response.
1. Chat history is stored in a local Postgres, and is also accesable via the API.
1. The API supports streaming of the response from the LLM.

This repo is built by Hipposys Ltd., and serves as a starting off point for new RAG projects for our clients. It is open sourced both for educational purposes, and to serve as a base for commercial projects.

The current skeleton contains support for using Amazon Bedrock as the LLM provider, and Milvus as the vector database. Additional LLM providers and vector databases are planned to be added in the near future.


## Features

- Web Server providing endpoints for:
    -  Adding and removing custom data.
    - Sending and receiving chat messages.
        - This supports streaming of the response from the LLM.
- Using Amazon Bedrock as an LLM provider.
- Milvus Vector database integration.
- Built on top of Langchain.
- Chat history is stored in a local Postgres, and is also accesable via the API.

## Prerequisites

Currently, you must have an Amazon Bedrock account to use this project.

You'll also need Docker for the local deploy.

## Contact

Looking for help or have questions? Contact us at [contact@hipposys.com](mailto:contact@hipposys.com).

We work with clients on a variety of AI engineering and Data Enngineering projects.

## Installation

The local deployment relies on having Docker installed.

It also relies on having access to Amazon Bedrock models, which are used as the LLM provider of the application.

### Setting up Bedrock
1. Make sure that you have a Bedrock model available in your AWS account:
    1. Log into the AWS console.
    1. Navigate to the `Amazon Bedrock` service.
    1. In the left navigration pane: `Bedrock configurations` -> `Model access`.
    1. We currently use `Claude 3.5 Sonnet` for inference and `Titan Text Embeddings V2` for embeddings.
        1. Note that this may change, you can either change it yourself, or see that someone else has changed it in the code.
        1. Note that these models may not be available in all regions, we currently use `us-east-1` (N. Virginia).
    1. If these models are not enabled, you'll have to ask for access. The access should be granted immediately upon request.
    1. You'll need to generate access credentials for your Amazon local for use in the application.

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
    1. For the initial run, the most important credentials are the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY. Other credentials are temporary and must be replaced with the correct ones when the application is deployed.
    1. You should also change the `FAST_API_ACCESS_SECRET_TOKEN` to a new random secret.
1. Build and run the project via Docker: `docker compose -f docker-compose.yml up -d --build`
1. After running docker, you should have multiple services running.
    1. You can check the status of the services with `docker ps -a`.
    1. Make sure the `rag-skeleton-fastapi` and `milvus-standalone` containers are running.
    1. You should also see a `postgres` container running.
1. Go to `localhost:8080/hello-world` to see an `{"hello": "world"}` response from the server.
1. You now have a running instance of the RAG application.


## Example Usage

We're now going to give a simple example of how to use the API. The plan is to:

1. Query our LLM, via the API, and ask for specific "inside" information, which it does not have access to.
1. Use the API to add the information to the vector database via simple textual data.
1. Query the LLM again and ask for the same information, which it now has access to.

Note that by default, the repo is configured to return simple textual responses in a streaming manner. For production it's recommended to return JSON-formatted responses instead.


### 1. Query the LLM via the API

The following command sends a chat query via the API.:

```bash
curl \
    -i \
    -X POST \
    --no-buffer \
    -b cookies.tmp.txt -c cookies.tmp.txt \
    -H 'x-access-token: 123' \
    -H 'Content-Type: application/json' \
    -d '{"message": "What headphones are recommended by the company for listening to podcasts?"}' \
    http://localhost:8080/chat/ask
```

Highlighting the important things in the command:
- We are hitting the '/chat/ask' endpoint to actually ask the LLM a question.
- We are specifying the access-token to be the default value that is in the .env file.
- We are using -b and -c to save the cookies from the server. This lets the server continue our chat session, so additional requests to /chat/ask will be part of the same chat session.
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
    -H 'x-access-token: 123' \
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
    -H 'x-access-token: 123' \
    -H 'Content-Type: application/json' \
    -d '{"source_id": "1001", "source_name": "Headphones Guide II", "text": "The recommended headphones to use while listening to music is BoseQC35", "modified_at": "2024-09-22T17:04"}' \
    http://localhost:8080/embeddings/text/store
```


Here, we are sending data to the /embeddings/text/store endpoint. This endpoint is responsible for storing the text data in the vector database. We store the data itself, as well as metadata about the source of the data - the source name, the source id, and the modification date.


### 3. Query the LLM again

Now we can query the LLM again and ask for the same information, which it now has access to:

```bash
curl \
    -i \
    -X POST \
    --no-buffer \
    -b cookies.tmp.txt -c cookies.tmp.txt \
    -H 'x-access-token: 123' \
    -H 'Content-Type: application/json' \
    -d '{"message": "What headphones are recommended by the company?"}' \
    http://localhost:8080/chat/ask
```

This time, you shold see a response from the LLM that includes the information we added to the vector database.

### Other API Endpoints

You can delete a source using the /embeddings/text/delete endpoint:
```bash
curl -i -X DELETE --no-buffer -b cookies.tmp.txt -c cookies.tmp.txt  -H 'x-access-token: 123' -H 'Content-Type: application/json' -d '{"source_id": "1001"}' http://localhost:8080/embeddings/text/delete
```


## Deploying to production

A more complete guide to deploying to production will be added later.

For now, note that you will need to:
1. You should consider changing the responses generated to `JSON` responses instead of textual responses in the codebase.
