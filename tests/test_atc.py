import itertools

from loguru import logger

from medsop.atc import ATCRec


def test_load_and_index_by_parent():
    top5: list[ATCRec] = list(itertools.islice(ATCRec.load(), 5))
    assert len(top5) == 5
    logger.info(f"{top5[4]=}")
    lookup: dict[str, ATCRec] = {i.class_id: i for i in top5}
    # here's the 6th line in the file
    # http://purl.bioontology.org/ontology/UATC/L03AA,Colony stimulating factors,,,false,C0009392,http://purl.bioontology.org/ontology/STY/T123|http://purl.bioontology.org/ontology/STY/T116,http://purl.bioontology.org/ontology/UATC/L03A,4,Y,http://purl.bioontology.org/ontology/STY/T123|http://purl.bioontology.org/ontology/STY/T116
    rec: ATCRec = lookup["L03AA"]
    assert rec is not None
    assert rec.class_id == "L03AA"
    assert rec.preferred_label == "Colony stimulating factors"
    assert rec.synonyms is None
    assert not rec.obsolete
    assert rec.cui == "C0009392"
    assert rec.semantic_types == ["T123", "T116"]
    assert rec.parents == ["L03A"]
    assert rec.atc_level is 4
    assert rec.is_drug_class == True  # pydantic normalizes 'Y' to True! :-)

    index_by_parent: dict[str, list[ATCRec]] = ATCRec.index_by_parent(top5)
    assert "L03A" in index_by_parent.keys()
    assert len(index_by_parent["L03A"]) > 0
    assert rec in index_by_parent["L03A"]

    # if worried about test speed, the following could be moved to an optionally run test.
    entire_file: dict[str, list[ATCRec]] = ATCRec.load_all()
    assert len(entire_file.keys()) > 100
