#!/usr/bin/fish
conda activate py38
# TO setup: mamba install pytorch cudatoolkit=11.3 -c pytorch -c nvidia
# poetry run uvicorn --host 0.0.0.0 app.main:app

export TRANSFORMERS_CACHE=./cache

export QA_DOCUMENTSTORE_PARAMS_HOST=10.120.10.131
export QA_DOCUMENTSTORE_PARAMS_PORT=57664
export QA_DOCUMENTSTORE_PARAMS_INDEX=data_nlp

export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_HOST=10.120.10.131
export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_PORT=57664
export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_INDEX=data_searchui

export SEARCH_SERVICES=search,qa,similarity,feedback
#54125

export SERVICES=$SEARCH_SERVICES

#embedding
##question-generation
#$SEARCH_SERVICES
#search
#embedding
#search,search,qa,,
#similarity,summarizer,langdetect

env \
  DISABLE_RUNTIME_TESTS=1 \
  NLP_SERVICES=$SERVICES\
  CONVERTER_TIKA_PARAMS_TIKA_URL=http://localhost:9998/tika \
  TOKENIZERS_PARALLELISM=false \
  uvicorn --workers=1 --host 0.0.0.0 app.main:app

#converter,search,qa,similarity,summarizer,zeroshot-classifier,spacy,question-generation
#
#,qa,search,question-classifier
#,question-classifier,summarizer,question-generation,zeroshot-classifier,ner
# ,
# question-generation,
# summarizer,spacy,zeroshot-classifier,ner
#,qa,,,summarizer
