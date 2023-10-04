---
sidebar_position: 7
---

# BondAI With Docker

## BondAI Docker Image

BondAI Docker images are available on [DockerHub here](https://hub.docker.com/r/krohling/bondai). If you intend to use tools that run arbitrary code (*PythonREPLTool*) or access your shell (*ShellTool*) it is highly recommended that you run BondAI in a Docker container as these tools can damage your machine.

Before running the BondAI Docker container it is recommended that you create a directory named 'agent-volume' and mount it as a volume on the container. This will be used as the Agent's working directory and allows you to easily share files with the Agent.

```bash
mkdir agent-volume
docker pull krohling/bondai:latest
docker run -it --rm \
           -v ./agent-volume:/agent-volume \
           -w /agent-volume \
           OPENAI_API_KEY=sk-XXXXXXXXXX \
           bondai:latest bondai
```

## BondAI with Docker Compose

The docker-compose.yml file is located in the ./docker directory of the Github repository and makes use of a .env file and a pre-configured volume which is mapped to an ./agent-volume directory.

There's also two options with Docker Compose. From the command line with this command:

```bash
cd ./docker
docker compose up
```

Or if you use vsCode, install the official Docker Extension, then right click on the ./docker/docker-compose.yml file and select Compose Up
