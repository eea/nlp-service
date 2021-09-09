FROM python:3.8.10

COPY . /app

RUN curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh
RUN bash Mambaforge-$(uname)-$(uname -m).sh -b

RUN ~/mambaforge/bin/mamba install pytorch cudatoolkit=10.2 tensorflow tensorflow-hub -c pytorch -y

RUN pip install https://github.com/deepset-ai/haystack/archive/master.zip

WORKDIR /app
RUN pip install -r requirements.txt
