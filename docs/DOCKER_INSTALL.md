# DOCKER INSTALL

From the project root

```bash
docker build --build-arg CACHEBUST=$(date +%s) -f docker-extra/Dockerfile -t bondai:latest .
```

This builds the latest version from the local source code

```bash
docker run -it -e OPENAI_API_KEY=************** bondai:latest bondai --enable-prompt-logging
```

Replace the ****** with your OpenAi API Key


# DOCKERHUB

```bash
 docker build --build-arg CACHEBUST=$(date +%s) -f docker-extra/Dockerfile -t bondai:latest . && docker push bondai:latest
 ```