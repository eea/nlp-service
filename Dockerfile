FROM nvcr.io/nvidia/tensorflow:21.08-tf2-py3

WORKDIR /app

RUN apt update
RUN apt install libgraphviz-dev graphviz -y

COPY requirements/ /app/requirements/
# RUN pip install --no-cache-dir -c requirements/constraints.txt -r requirements/gpu.txt
RUN pip install --no-cache-dir -r requirements/haystack-1.11.txt

RUN python -m spacy download en_core_web_sm
RUN python -m spacy download en_core_web_trf

COPY . /app
RUN mkdir -p /app/var

# define the default command to run when starting the container
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "app.main:app"]
