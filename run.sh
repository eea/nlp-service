#!/bin/sh
# poetry run uvicorn --host 0.0.0.0 app.main:app

NLP_SERVICES=qa TOKENIZERS_PARALLELISM=false uvicorn --workers=1 --host 0.0.0.0 app.main:app
#,search,embedding,question-classifier
#NLP_SERVICES=question-classifier
