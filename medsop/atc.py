import csv
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel, Field

from medsop.settings import MOPSettings

settings = MOPSettings()


class ATCRec(BaseModel):
    class_id: str = Field(None, alias="Class ID")
    preferred_label: str = Field(None, alias="Preferred Label")
    synonyms: str = Field(None, alias="Synonyms")
    definitions: str = Field(None, alias="Definitions")
    obsolete: bool = Field(False, alias="Obsolete")
    cui: str = Field(None, alias="CUI")
    semantic_types: list[str] = Field(list, alias="Semantic Types")
    parents: list[str] = Field([], alias="Parents")
    atc_level: int = Field(-1, alias="ATC LEVEL")
    is_drug_class: bool = Field(False, alias="Is Drug Class")

    class Config:
        allow_population_by_field_name = True

    # Here are the columns. Note that 'Semantic types', 'Parents' and 'Semantic type UMLS property' are 0...n fields, delimited by '|'
    # Class ID,Preferred Label,Synonyms,Definitions,Obsolete,CUI,Semantic Types,Parents,ATC LEVEL,Is Drug Class,Semantic type UMLS property
    # http://purl.bioontology.org/ontology/UATC/C07CA02,oxprenolol and other diuretics,,,false,C3653011,http://purl.bioontology.org/ontology/STY/T121|http://purl.bioontology.org/ontology/STY/T109,http://purl.bioontology.org/ontology/UATC/C07CA,5,,http://purl.bioontology.org/ontology/STY/T121|http://purl.bioontology.org/ontology/STY/T109
    # Here's the above line, with whitespace introduced to make it more readable:
    # http://purl.bioontology.org/ontology/UATC/C07CA02,oxprenolol and other diuretics,,,false,C3653011,
    # http://purl.bioontology.org/ontology/STY/T121|http://purl.bioontology.org/ontology/STY/T109,
    # http://purl.bioontology.org/ontology/UATC/C07CA,5,,
    # http://purl.bioontology.org/ontology/STY/T121|http://purl.bioontology.org/ontology/STY/T109
    #
    # We will shorten the IDs to only include everything to the right on the final forward slash
    @staticmethod
    def load() -> Iterable["ATCRec"]:
        def strip_url(v: str) -> str:
            return v[v.rindex("/") + 1 :]

        def normalize_id_lists(key: str, value: str) -> str | list[str]:
            if "http:" in value:
                if key == "Class ID":
                    return strip_url(value)
                else:
                    return [strip_url(i) for i in value.split("|")]
            else:
                return value

        with open(Path(settings.atc_path)) as f:
            for d in csv.DictReader(f):
                tmp_dict = {
                    k: normalize_id_lists(k, v) for k, v in d.items() if v != ""
                }  # empty values problematic, also handle ID lists.
                r = ATCRec(**tmp_dict)
                yield (r)

    @staticmethod
    def index_by_parent(recs: list["ATCRec"]) -> dict[str, list["ATCRec"]]:
        ret: dict[str, list[ATCRec]] = defaultdict(list)
        for rec in recs:
            for p in rec.parents:
                ret[p].append(rec)
        return ret

    @staticmethod
    def load_all() -> dict[str, list["ATCRec"]]:
        return ATCRec.index_by_parent([r for r in ATCRec.load()])
