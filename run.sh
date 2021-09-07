#!/bin/sh
# poetry run uvicorn --host 0.0.0.0 app.main:app

TOKENIZERS_PARALLELISM=false uvicorn --workers=1 --host 0.0.0.0 app.main:app
