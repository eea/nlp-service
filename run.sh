#!/usr/bin/fish
conda activate py38
# poetry run uvicorn --host 0.0.0.0 app.main:app

# export QA_DOCUMENTSTORE_PARAMS_HOST=10.120.10.131
# export QA_DOCUMENTSTORE_PARAMS_PORT=54125
# export QA_DOCUMENTSTORE_PARAMS_INDEX=data_nlp
#
# export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_HOST=10.120.10.131
# export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_PORT=54125
# export SEARCH_FACETEDDOCUMENTSTORE_PARAMS_INDEX=data_searchui

#
export SERVICES=search
# summarizer,langdetect,converter,search,qa,similarity

env \
  DISABLE_RUNTIME_TESTS=1 \
  NLP_SERVICES=$SERVICES\
  CONVERTER_TIKA_PARAMS_TIKA_URL=http://localhost:9998/tika \
  TOKENIZERS_PARALLELISM=false \
  uvicorn --workers=1 --host 0.0.0.0 app.main:app

#converter,search,qa,similarity,summarizer
#
#,qa,search,question-classifier
#,question-classifier,summarizer,question-generation,zeroshot-classifier,ner
# embedding,
# question-generation,
# summarizer,spacy,zeroshot-classifier,ner
#,qa,,,summarizer
