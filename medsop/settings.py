from pydantic import BaseSettings

from medsop.file_utils import ROOT_DIR


class MOPSettings(BaseSettings):
    atc_path: str = f"{ROOT_DIR}/ATC.csv"
    drug_review_dir = f"{ROOT_DIR}/../drug-reviews"
    drug_review_conditions: list[str] = ["High Cholesterol"]
    drug_review_drugs: list[str] = []
