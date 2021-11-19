#!/bin/sh
# poetry run uvicorn --host 0.0.0.0 app.main:app

NLP_SERVICES=converter TOKENIZERS_PARALLELISM=false uvicorn --workers=1 --host 0.0.0.0 app.main:app
#DISABLE_RUNTIME_TESTS=1
#search,qa,qa,search,question-classifier,similarity
#,question-classifier,summarizer,question-generation,zeroshot-classifier,ner
# embedding,
# question-generation,
# summarizer,spacy,zeroshot-classifier,ner
#,qa,,,summarizer
