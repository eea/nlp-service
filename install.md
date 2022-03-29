# Installation Steps

* **Install Anaconda**

https://docs.anaconda.com/anaconda/install/index.html

https://linuxize.com/post/how-to-install-anaconda-on-ubuntu-20-04/

Please note that after the installation there will be automatically created a conda  ``base`` environment  

* **Clone the repository**

```shell
git clone https://github.com/eea/nlp-service.git -b develop
cd nlp-service/
```
* **Install Mamba**

```shell
conda install mamba -n base -c conda-forge
```

* **Create a conda environment**

```shell
conda create -n py38 python=3.8
```

* **Edit Anaconda Configuration File**

```shell
vim <PATH>/.config/fish/config.fish
```
*PATH is the path where ``config.fish``, the Anaconda configuration file, was added after the installation*

Inside ``config.fish`` add the following line:
```shell
set PATH <PATH TO ANACONDA FOLDER>/anaconda3/bin $PATH
```
More info here: https://stackoverflow.com/questions/34280113/add-conda-to-path-in-fish

* **Restart the terminal**

* **Activate conda environment**

```shell
cd nlp-service/
conda activate py38
```
* **Initialize Conda**

```shell
conda init fish
```

* **Install the packages**

```shell
mamba install pytorch cudatoolkit=10.2 tensorflow tensorflow-hub -c pytorch
conda install pytorch torchvision cudatoolkit=10.2 -c pytorch
```

 *Please note that ``cudatoolkit`` version may be different based on your system configuration*

 *More info here: https://pytorch.org/get-started/locally/*

* **Install ``pip`` using ``conda``**

```shell
conda install pip
```
*Please note that this step should be done while ``py38`` environment is activated.*

This step is necessary in order to bypass the compatibility issues between ``conda`` and ``pip``.

More info: https://www.anaconda.com/blog/using-pip-in-a-conda-environment

* **Install NLP Service requirements**

```shell
pip install -e .
```

* **Install Jupyter Lab**

```shell
pip install --user ipykernel
python -m ipykernel install --user --name=py38
conda install -c conda-forge jupyterlab
```
More info here:
https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html

* **Start Jupyter Lab**

```shell
 jupyter lab
```

* ***Select Conda ``py38`` environment as Jupyter Kernel***

Go to Jupyter Lab opened in the browser
``http://localhost:8888``

Go to ``Kernel -> Change Kernel -> py38``

More info:
https://moonbooks.org/Articles/How-to-use-a-specific-python-conda-environment-in-a-Jupyter-notebook-/

# Common issues

### Installed packages inside the environment won't import in jupyter lab / notebook ###
https://github.com/jupyter/notebook/issues/2359

If the above problem is encountered when running Jupyter notebooks, please execute the following commands:

* **Open a new terminal and DO NOT activate yet the ``py38`` conda env**


* **Reinstall pip using conda**

```shell
cd nlp-service/
conda install -n py38 pip
```
* **Activate the ``py38`` env**

```shell
conda activate py38
```
* **Run again the commands to reinstall the requirements**

```shell
pip install -e .
conda install pytorch torchvision cudatoolkit=10.2 -c pytorch
```
Please note that ``cudatoolkit`` version may be different based on your system configuration

 *More info: https://pytorch.org/get-started/locally/*
