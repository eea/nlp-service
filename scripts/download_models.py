#!/usr/bin/python

import glob
import os
import subprocess

import git
import yaml
from git import RemoteProgress
from tqdm import tqdm
from yamlinclude import YamlIncludeConstructor


class CloneProgress(RemoteProgress):
    def __init__(self):
        super().__init__()
        self.pbar = tqdm()

    def update(self, op_code, cur_count, max_count=None, message=""):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()


class DownloadTransformerModels:
    PATH = "/app/conf/"

    PATH_TO_CLONE = "/app/models/"

    YamlIncludeConstructor.add_to_loader_class(loader_class=yaml.SafeLoader, base_dir=PATH)

    def __init__(self):
        self.models = []

    def get_yml_files(self):
        files = []
        if not self.PATH:
            return files
        else:
            files = glob.glob(self.PATH + "*.yml")

        return files

    def check_component(self, component):
        if "type" in component:
            if "Transformer" in component["type"] or "FARMReader" in component["type"]:
                if "params" in component:
                    params = component["params"]

                    if "model_name_or_path" in params:
                        if params["model_name_or_path"]:
                            model_name_or_path = params["model_name_or_path"]
                            model = model_name_or_path[-(len(model_name_or_path) - len(self.PATH_TO_CLONE)):]
                            if model not in self.models:
                                self.models.append(model)

                    # if "model" in params:
                    #    if params["model"] not in t_models:
                    #        model_tokens = params["model"].split("/")
                    #        if len(model_tokens) == 2:
                    #            t_models.append(params["model"])
                    #        else:
                    #            print("Model Error")

    def get_models(self, parsed_yaml):
        if parsed_yaml:
            if "components" in parsed_yaml:
                for component in parsed_yaml["components"]:
                    self.check_component(component)

    def process_files(self):
        yml_files = self.get_yml_files()

        for file in yml_files:
            print(f"Searching for transformer models in file {file}...")
            with open(file, "r") as stream:
                try:
                    parsed_yaml = yaml.safe_load(stream)
                    self.get_models(parsed_yaml)
                except yaml.YAMLError as exc:
                    print(exc)

        return True

    def clone(self):
        for model in self.models:

            repo_url = f"https://huggingface.co/{model}"

            print("VOM testa daca exista calea " + str(f"{self.PATH_TO_CLONE}{model}"))
            if not os.path.exists(f"{self.PATH_TO_CLONE}{model}"):
                print("Cica nu exista calea " + str(f"{self.PATH_TO_CLONE}{model}"))
                print(f"Cloning model {model} ....")
                git.Repo.clone_from(repo_url, f"{self.PATH_TO_CLONE}{model}", progress=CloneProgress())
                print("Running `git lfs install` ....")
                subprocess.call("git lfs install", shell=True, cwd=f"{self.PATH_TO_CLONE}{model}")
                print("Running `git lfs pull` ....")
                subprocess.call("git lfs pull", shell=True, cwd=f"{self.PATH_TO_CLONE}{model}")
            else:
                print(f"Skipping! The repository for model {model} is already cloned.")


        print("Cloning ended successfully!")

    def run(self):
        self.process_files()
        self.clone()


if __name__ == "__main__":
    DownloadTransformerModels().run()
