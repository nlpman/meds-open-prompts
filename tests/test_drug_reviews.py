import csv
import itertools
from pathlib import Path

from loguru import logger

from medsop.settings import MOPSettings

settings = MOPSettings()

from medsop.drug_reviews import (
    stream_drug_reviews,
    analyze_drugs_and_conditions,
    split_training_for_annotation,
    SupervisionDrugReview,
    RankDrugReview,
)


def test_load_drug_reviews():
    top5 = list(itertools.islice(stream_drug_reviews(), 5))
    assert len(top5) == 5
    logger.info(f"{top5[4]=}")
    assert top5[0].condition == "High Cholesterol"


def test_analyze_stream():
    # hc_drs = list(stream_drug_reviews(conditions=["High Cholesterol"]))
    # analyze_stream(hc_drs)
    analyze_drugs_and_conditions(conditions=["High Cholesterol"])


def test_split_training_for_annotation():
    out_dir_name = "test_out"
    dir = Path(out_dir_name)
    if dir.exists():
        for f in dir.iterdir():
            f.unlink()
        dir.rmdir()

    file_paths: dict[str, str] = split_training_for_annotation(output_dir=out_dir_name)
    assert dir.exists()
    with open(file_paths["super"], "r") as fp:
        reader = csv.DictReader(fp)
        for r in reader:
            sdr = SupervisionDrugReview(**r)
            assert sdr.condition in settings.drug_review_conditions
            break
    with open(file_paths["rank"], "r") as fp:
        reader = csv.DictReader(fp)
        for r in reader:
            rdr = RankDrugReview(**r)
            assert rdr.condition in settings.drug_review_conditions
            break
    # for f in dir.iterdir():
    #     with open(f, "r") as f:
    #         reader = csv.DictReader(f)
    #         for r in reader:
    #             dr = DrugReview(**r)
    #             assert dr.condition in settings.drug_review_conditions
    #         break
