# EEA SemanticSearch NLP Service

## Requirements

Python 3.6+, a GPU-powered server

##

By default it would operate the following endpoints (go to
[local OpenAPI page](http://localhost:8000/docs) for an overview):

- **embedding**: return sentence embedding using Facebook's dual head encoder
  models used by Haystack for QA.
- **ner**: a NER model. WIP
- **similarity**: Compute similarity between sentences
- **zeroshot-classifier**: Classifiy text according to provided possible
  categories
- **question-classifier**: Classify phrases in two categories:
  question/statement
- **question-generation**: Generate questions and possible answers based on
  provided text
- **summarizer**: Automatically summarize text

<!-- ## Installation/Setup -->
<!-- Makefile provided to get you up and going quickly. -->
<!-- ```bash -->
<!-- make setup -->
<!-- ``` -->
<!--  -->
<!-- ## Run It -->
<!-- 1. Start your  app with: -->
<!-- ```bash -->
<!-- poetry run uvicorn app.main:app -->
<!-- ``` -->
<!--  -->
<!-- 2. Go to [http://localhost:8000/docs](http://localhost:8000/docs). -->
<!--  -->
<!-- 3. You can use the sample payload from the `docs/sample_payload.json` file when trying out the house price prediction model using the API. -->
<!--    ![Prediction with example payload](./docs/sample_payload.png) -->
<!--  -->
<!-- ## Testing -->
<!-- Makefile provided to provide test suite. -->
<!-- ```bash -->
<!-- make test -->
<!-- ``` -->
<!--  -->
<!-- ## Linting & Formatting -->
<!-- Makefile provided to provide linting & formatting suite. -->
<!-- ```bash -->
<!-- make format -->
<!-- ``` -->
