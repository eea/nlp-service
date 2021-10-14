#!/bin/sh
# poetry run uvicorn --host 0.0.0.0 app.main:app

NLP_SERVICES=qa,search,question-classifier,similarity TOKENIZERS_PARALLELISM=false uvicorn --workers=1 --host 0.0.0.0 app.main:app
#
# embedding,
# question-generation,
# summarizer,spacy,zeroshot-classifier,ner
#,qa,,,summarizer
