## Requirements

It is highly recommended to run this with GPUs and Nvidia GPUs in particular. You can run any LLM you want that is listed on huggingface, but many will not be feasible in a local environment to run in a reasonable timeframe without GPU support. Without GPU support I would recommend GPT-2 or similar.

The API is much easier to install with docker and docker-compose
## Installation

Install through the command 

```pip install -f requirements.txt```

## Folders

```/docker``` contains Docker file for the rest server

```/rest_server``` contains code for the API and code to query the API
