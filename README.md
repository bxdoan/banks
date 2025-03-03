# API for check MBBanks Transaction


## Features

- `/health` endpoint for health checking
- `/transaction` for get balance and transaction
- CORS enabled

## Local Development

### Installation

#### Option 1: Using pip

```bash
pip install -r requirements.txt
```

#### Option 2: Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a faster Python package installer and resolver.

1. Install uv if you don't have it:
```bash
pip install uv
```

2. Install dependencies using uv:
```bash
uv pip install -r requirements.txt
```

Or use uv sync:
```bash
uv sync
```

### Running the server

```bash
uvicorn main:app --reload
```

3. Access the API at http://localhost:8000

## Deployment

This API is configured for deployment on Vercel. To deploy:

1. Push this repository to GitHub
2. Connect your GitHub repository to Vercel
3. Vercel will automatically detect the configuration and deploy the API

## API Documentation

Once deployed, you can access the API documentation at `/docs` endpoint.
