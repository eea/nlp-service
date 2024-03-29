#!/usr/bin/fish
conda activate py38
# TO setup: mamba install pytorch cudatoolkit=11.3 -c pytorch -c nvidia
# poetry run uvicorn --host 0.0.0.0 app.main:app

export TRANSFORMERS_CACHE=./cache

# http://10.120.10.204:60168/
# 10.120.10.204:57664

export QA_FACETEDDOCUMENTSTORE_PARAMS_HOST=10.120.10.204
export QA_FACETEDDOCUMENTSTORE_PARAMS_PORT=60168
export QA_FACETEDDOCUMENTSTORE_PARAMS_INDEX=data_searchui
export QA_FACETEDDOCUMENTSTORE_PARAMS_EMBEDDING_FIELD=embedding
export QA_FACETEDDOCUMENTSTORE_PARAMS_NLP_PATH=nlp_250
export QA_FACETEDDOCUMENTSTORE_PARAMS_CONTENT_FIELD=text
export QA_FACETEDDOCUMENTSTORE_PARAMS_NESTED_CONTENT_FIELD=text

export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_HOST=10.120.10.204
export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_PORT=60168
export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_INDEX=data_searchui
export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_EMBEDDING_FIELD=embedding
export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_CONTENT_FIELD=text
export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_NESTED_CONTENT_FIELD=text

export FEEDBACK_FEEDBACKSTORE_PARAMS_HOST=10.120.10.204
export FEEDBACK_FEEDBACKSTORE_PARAMS_PORT=60168
export FEEDBACK_FEEDBACKSTORE_PARAMS_INDEX=data_searchui_datahub
export FEEDBACK_FEEDBACKSTORE_PARAMS_LABEL_INDEX=data_searchui_datahub-feedback
export FEEDBACK_FEEDBACKSTORE_PARAMS_CREATE_INDEX=True


export SEARCH_SERVICES=feedback,qa,search,similarity,qasearch,embedding

export SERVICES=$SEARCH_SERVICES

env \
  DISABLE_RUNTIME_TESTS=1 \
  NLP_SERVICES=$SERVICES\
  CONVERTER_TIKA_PARAMS_TIKA_URL=http://localhost:9998/tika \
  TOKENIZERS_PARALLELISM=false \
  uvicorn --workers=1 --host 0.0.0.0 app.main:app

