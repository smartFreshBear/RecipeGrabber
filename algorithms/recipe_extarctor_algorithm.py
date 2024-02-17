"""
ExtractorAlgorithm Interface class
with one method: extract
"""
from abc import ABC


class ExtractorAlgorithm(ABC):
    def extract(self, all_text: str) -> (str, str):
        pass
