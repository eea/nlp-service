# EEA AI NLP Service

## Requirements

Python 3.6+, a GPU-powered server

By default it would operate the following endpoints (go to
[local OpenAPI page](http://localhost:8000/docs) for an overview):

- **embedding**: return sentence embedding using Facebook's dual head encoder
  models used by Haystack for QA.
- **ner**: a NER model. WIP
- **similarity**: Compute similarity between sentences
- **zeroshot-classifier**: Classifiy text according to provided possible
  categories
- **qa**: Question and answer model
- **question-classifier**: Classify phrases in two categories:
  question/statement
- **question-generation**: Generate questions and possible answers based on
  provided text
- **summarizer**: Automatically summarize text

You can customize which services to start via an environment variable:

```bash
export NLP_SERVICES="embedding,ner,summarizer"
```

## Instalation

```
	conda install mamba -n base -c conda-forge
	conda create -n py38 python=3.8
	conda init fish
	conda activate py38
	mamba install pytorch cudatoolkit=10.2 tensorflow tensorflow-hub -c pytorch
	pip install -e .
```

## Copyright and license

The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

See [LICENSE](https://github.com/eea/nlp-service/blob/master/LICENSE) for details.

## Funding

[European Environment Agency (EU)](http://eea.europa.eu)
