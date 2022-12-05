#!/usr/bin/fish
conda activate py38
# TO setup: mamba install pytorch cudatoolkit=11.3 -c pytorch -c nvidia
# poetry run uvicorn --host 0.0.0.0 app.main:app

export TRANSFORMERS_CACHE=./cache

# http://10.120.10.204:60168/
# 10.120.10.131:57664

export QA_FACETEDDOCUMENTSTORE_PARAMS_HOST=10.120.10.204
export QA_FACETEDDOCUMENTSTORE_PARAMS_PORT=60168
export QA_FACETEDDOCUMENTSTORE_PARAMS_INDEX=data_searchui
export QA_FACETEDDOCUMENTSTORE_PARAMS_EMBEDDING_FIELD=embedding
export QA_FACETEDDOCUMENTSTORE_PARAMS_CONTENT_FIELD=fulltext
export QA_FACETEDDOCUMENTSTORE_PARAMS_NESTED_CONTENT_FIELD=text

export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_HOST=10.120.10.204
export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_PORT=60168
export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_INDEX=data_searchui
export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_EMBEDDING_FIELD=embedding_field
export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_CONTENT_FIELD=fulltext

export FEEDBACK_FEEDBACKSTORE_PARAMS_HOST=10.120.10.204
export FEEDBACK_FEEDBACKSTORE_PARAMS_PORT=60168
export FEEDBACK_FEEDBACKSTORE_PARAMS_INDEX=data_searchui
export FEEDBACK_FEEDBACKSTORE_PARAMS_LABEL_INDEX=data_searchui-feedback
export FEEDBACK_FEEDBACKSTORE_PARAMS_CREATE_INDEX=True

export SEARCH_SERVICES=feedback,qa,search,similarity,qasearch
export SERVICES=$SEARCH_SERVICES,langdetect

#,qasearch
#search,
#search,qa,,
#54125


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
  #--reload

#converter,search,qa,similarity,summarizer,zeroshot-classifier,spacy,question-generation
#
#,qa,search,question-classifier
#,question-classifier,summarizer,question-generation,zeroshot-classifier,ner
# ,
# question-generation,
# summarizer,spacy,zeroshot-classifier,ner
#,qa,,,summarizer
