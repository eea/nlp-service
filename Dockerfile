FROM nvcr.io/nvidia/tensorflow:21.08-tf1-py3

COPY . /app

RUN curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh
RUN bash Mambaforge-$(uname)-$(uname -m).sh -b

RUN ~/mambaforge/bin/mamba install pytorch cudatoolkit=10.2 tensorflow tensorflow-hub -c pytorch -y

RUN pip3 install https://github.com/deepset-ai/haystack/archive/master.zip
#RUN pip3 install spacy

#RUN python3 -m spacy download en_core_web_sm en_core_web_trf

WORKDIR /app
RUN pip3 install -r requirements.txt

# define the default command to run when starting the container
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "app.main:app"]
