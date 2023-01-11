import csv
from itertools import islice
from pathlib import Path
from typing import Counter, Iterable

import typer
from loguru import logger
from pydantic import BaseModel, Field, ValidationError

from medsop.settings import MOPSettings

tapp = typer.Typer()
settings = MOPSettings()


class DrugReview(BaseModel):
    # row_id:str|None = None
    row_id: str = Field(None, alias="Unnamed: 0")
    drug_name: str = Field(None, alias="drugName")
    condition: str | None
    review: str
    rating: int
    # date:datetime
    useful_count: int = Field(-1, alias="usefulCount")

    class Config:
        allow_population_by_field_name = True


class SupervisionDrugReview(DrugReview):
    complaint: str = ""
    credibility: str = ""


class RankDrugReview(DrugReview):
    model_version: str = ""
    gpt2: str = ""
    t5: str = ""
    preference = ""


def default_filter(dr: DrugReview) -> bool:
    return dr.condition in settings.drug_review_conditions


def stream_drug_reviews(
    train: bool = True,
    conditions: list[str] = settings.drug_review_conditions,
    drugs: list[str] = settings.drug_review_drugs,
) -> Iterable[DrugReview]:
    logger.info("starting")
    split_name = "train" if train else "test"
    with open(Path(f"{settings.drug_review_dir}/{split_name}.jsonl")) as f:
        for ndx, line in enumerate(f):

            dr = DrugReview.parse_raw(line)
            logger.info(f"{ndx=} {dr=}")
            # dr.row_id = f"{split_name}_{ndx}"
            if (len(conditions) == 0 or dr.condition in conditions) and (
                len(drugs) == 0 or dr.drug_name in drugs
            ):
                yield dr


def analyze_stream(stream: Iterable[DrugReview]):
    """writes histograms of drug names and conditions to log files"""
    condition_counter = Counter[str]()
    drug_counter = Counter[str]()
    for dr in stream:
        condition_counter[f"{dr.condition}"] += 1
        drug_counter[f"{dr.drug_name}"] += 1
    logger.info(f"{condition_counter=}")
    logger.info(f"{drug_counter=}")


@tapp.command()
def analyze_drugs_and_conditions(conditions: list[str] = [], drugs: list[str] = []):
    analyze_stream(stream_drug_reviews(conditions=conditions, drugs=drugs))


@tapp.command()
def split_training_for_annotation(output_dir: str = "batches") -> dict[str, str]:
    """splits examples into supervision and ranking spreadsheets, for annotations with
    names 'dr_training_supervision.csv' and 'dr_training_ranking.csv'.
    Both spreadsheets have an additional field called 'row_id', that represents the original row number in the training spreadsheet.

    The supervision spreadsheet have the following 2 additional columns added -- which the annotator will fill in:
    1) complaint -- a copy of the review -- the annotator will add <c> and </c> to mark the boundaries for the complaint related to the drug
    2) credibility -- the annotators intuitive guess about whether the complaints are related to the medication -- valid annotations are 'L','M', and 'H' for low, medium and high

    For the ranking spreadsheet, we will add columns for the GPT2 and T5 model outputs, and a preference column. So column names: "GPT2", "T5" and preference. The annotator will
    populate the preference column with "G","T", "B", or "N" for GPT2, T5, "both", and "neither". (NO
    """
    outdir = Path(output_dir)
    if not outdir.exists():
        outdir.mkdir()
    next_supervision: bool = True
    super_path = f"{output_dir}/dr_training_supervision.csv"
    rank_path = f"{output_dir}/dr_training_rank.csv"
    if Path(super_path).exists() or Path(rank_path).exists():
        print(f"Aborting: {super_path=} and/or {rank_path=} already exists")
        return

    with open(super_path, "w") as super_fp, open(rank_path, "w") as rank_fp:
        super_writer = csv.DictWriter(
            super_fp,
            fieldnames=list(
                SupervisionDrugReview.schema(by_alias=False)["properties"].keys()
            ),
        )
        super_writer.writeheader()
        rank_writer = csv.DictWriter(
            rank_fp,
            fieldnames=list(RankDrugReview.schema(by_alias=False)["properties"].keys()),
        )
        rank_writer.writeheader()
        for rec in stream_drug_reviews():
            if next_supervision:
                sdr = SupervisionDrugReview(**rec.dict())
                sdr.complaint = sdr.review
                super_writer.writerow(sdr.dict())
            else:
                rdr = RankDrugReview(**rec.dict())
                rank_writer.writerow(rdr.dict())
            next_supervision = not next_supervision
    return {"super": super_path, "rank": rank_path}


# @tapp.command()
# def batch_mentions(output_dir:str="batches", number_per_batch:int=10):
#     outdir = Path(output_dir)
#     if not outdir.exists():
#         outdir.mkdir()
#     fieldnames = list(DrugReview.schema(by_alias=False)["properties"].keys())
#
#     name = f"Conditions__{'_'.join(settings.drug_review_conditions)}_Drugs__{'_'.join(settings.drug_review_drugs)}"
#     def next_chunk(stream):
#         return list(islice(stream, number_per_batch))
#     ndx = 0
#     drstream = stream_drug_reviews()
#     while True:
#         ndx += 1
#         chunk = next_chunk(drstream)
#         if chunk is None or len(chunk) == 0:
#             break
#         logger.info(f"{len(chunk)=}")
#         with open(f"{output_dir}/{name}_{ndx}.csv", "w") as fp:
#             writer = csv.DictWriter(fp, fieldnames=fieldnames)
#             writer.writeheader()
#             for rec in chunk:
#                 logger.info(f"{rec=}")
#                 writer.writerow(rec.dict())


if __name__ == "__main__":
    tapp()
