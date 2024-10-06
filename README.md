# My RAG App

## Installation

1. Create a Python virtual environment with `Python 3.11`. I use conda, but you can use whatever you prefer:
    1. `conda -n my-rag-app python=3.11`
    1. `conda activate my-rag-app`
1. Install the requirements inside the environment: `pip install -r requirements.txt`
1. Add the files you'd like to index to the `data` directory.
    1. Note that currently we accept only `.docx` files. In addition, you must provide an `index.csv` file
        that contains the following columns `Name,ID,Type,Modified Time,Size (bytes),Extension,URL`.
1. Make sure that you have a Bedrock model available in your AWS account:
    1. Log into the AWS console.
    1. Navigate to the `Amazon Bedrock` service.
    1. In the left navigration pane: `Bedrock configurations` -> `Model access`.
    1. We currently use `Claude 3.5 Sonnet` for inference and `Titan Text Embeddings V2` for embeddings.
        1. Note that this may change, you can either change it yourself, or see that someone else has changed it in the code.
        1. Note that these models may not be available in all regions, we currently use `us-east-1` (N. Virginia).
    1. If these models are not enabled, you'll have to ask for access. The access should be granted immediately upon request.
1. Create an `.env` file:
    1. `cp .env-template .env`
    1. Fill it in with the necessary credentials and settings.

## Running

### From Notebook - easiest.

1. Milvus server:
    1. Make sure that you have Docker installed and running.
    1. Start Milvus in Docker by running: `bash milvus/standalone_embed.sh start`
1. Start Jupyter Lab: `jupyter lab`. This should open your browser with this project.
1. Open the notebook `vector-db-setup.ipynb` and run all of the cells in order to load the data from the files into the vector DB.

    Note that you've don't have to rerun this step every time. Only if you started a new vector DB or changed the contents of the `data` directory and would like to reload it.
1. Open and run the notebook `search-chat-bot.ipynb`.

### FastAPI Service

1. Update your `.env` file:
    1. `MILVUS_SERVER_URI='http://milvus-standalone:19530'` should be set
1. Make sure you have Docker installed and running.
1. Run `docker compose -f docker-compose.yml up -d --build`
1. Make sure the `server` and `milvus-standalone` containers are running: `docker ps -a`.
1. Go to `localhost:8080/hello-world` to see an `{"hello": "world"}` response from the server.
1. Go to `localhost:8880` to open Jupyter Lab.
    1. If it asks you for a token, run `
1. Start a conversation by running:
    ```Bash
    curl -i -X POST --no-buffer -c cookies.tmp.txt -b cookies.tmp.txt -H 'Content-Type: application/json' -d '{"message": "my question"}' http://localhost:8080/chat/ask
    ```
1. To create a new conversation:
    1. Restart the server container `docker compose restart server`
    1. Run:
    
    ```Bash
    curl -i -X POST --no-buffer -c cookies.tmp.txt -b cookies.tmp.txt -H 'Content-Type: application/json' http://localhost:8080/chat/new
    ```
