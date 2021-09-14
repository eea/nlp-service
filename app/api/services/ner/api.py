""" FastAPI data models for zeroshot classifier

See https://huggingface.co/cross-encoder/nli-roberta-base
"""

from typing import List

from pydantic import BaseModel


class NERRequest(BaseModel):
    text: str = "EEA Executive Director Hans Bruyninckx welcomed President Čaputová and her delegation, which also included Andrej Doležal, Slovakia’s Minister of Transport and Construction. The Executive Director thanked the President for Slovakia’s strong commitment to the EU’s environmental goals and explained how the EEA is working to provide reliable data and information to policymakers - specifically in supporting the European Green Deal and accompanying legislation, which aims to shift Europe towards a sustainable, low-carbon future."


class NERResponse(BaseModel):
    entities: List[dict]
