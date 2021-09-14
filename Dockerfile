FROM nvcr.io/nvidia/tensorflow:21.08-tf2-py3

COPY . /app

#RUN curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh
#RUN bash Mambaforge-$(uname)-$(uname -m).sh -b

#RUN ~/mambaforge/bin/mamba install pytorch cudatoolkit=10.2 tensorflow tensorflow-hub -c pytorch -y

RUN pip install https://github.com/deepset-ai/haystack/archive/da5ed437342e68c36ff68b1459462ae460382487.zip
RUN pip install spacy[cuda102]
WORKDIR /app
RUN pip install -r requirements.txt

RUN python -m spacy download en_core_web_sm
RUN python -m spacy download en_core_web_trf


# define the default command to run when starting the container
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "app.main:app"]
