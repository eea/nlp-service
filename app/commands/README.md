# Command line utilities

We have the following command line utilities:

## `app/commands/preprocess`

Given an ES index, it uses haystack to process it, split text and create a haystack compatible index

```
python app/commands/preprocess.py data_searchui "description" data_searchui-documents --split-length 500
```

## `app/commands/embed`

Given an ES index it produces and writes the text embeddings. Use it like:

```
python app/commands/embed.py data_searchui-documents text text_embeddings
```
