#!/bin/sh
# poetry run uvicorn --host 0.0.0.0 app.main:app

env TOKENIZERS_PARALLELISM=false
uvicorn --host 0.0.0.0 app.main:app
