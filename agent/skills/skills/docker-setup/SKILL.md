---
name: docker-setup
description: Create Dockerfiles and docker-compose files to containerize applications. Use when the user wants to run their project in Docker or prepare it for deployment.
---

# Docker Setup

## Standard Dockerfile (Python)
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Standard Dockerfile (Node.js)
```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --production

COPY . .

EXPOSE 3000
CMD ["node", "server.js"]
```

## docker-compose.yml Template
```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

## Useful Commands
```bash
docker compose up -d        # start everything
docker compose logs -f app  # watch app logs
docker compose down -v      # stop and remove volumes
docker exec -it <container> bash  # shell into container
```

## Best Practices
- Always use `.dockerignore` to exclude `node_modules`, `.env`, `.git`
- Pin base image versions (`python:3.12` not `python:latest`)
- Use multi-stage builds to reduce image size for production
