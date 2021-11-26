#!/bin/sh
# poetry run uvicorn --host 0.0.0.0 app.main:app

NLP_SERVICES=converter,search,qa,similarity \
  CONVERTER_TIKA_PARAMS_TIKA_URL=http://localhost:9998/tika \
  TOKENIZERS_PARALLELISM=false \
  uvicorn --workers=1 --host 0.0.0.0 app.main:app
#DISABLE_RUNTIME_TESTS=1
#,qa,search,question-classifier
#,question-classifier,summarizer,question-generation,zeroshot-classifier,ner
# embedding,
# question-generation,
# summarizer,spacy,zeroshot-classifier,ner
#,qa,,,summarizer
