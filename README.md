# Meds Open Prompt
An exploration of Prompt Learning ( https://thegradient.pub/prompting/ ) in a medical domain, 
with a focus on surfacing common side effects for drugs. 
Prompt learning is a technique to improve the results from zero-shot learning on large language models.

The model used is

Atorvastatin is a drug for high cholesterol. Patient experienced [MASK] after starting atorvastatin.

# Setup
## Virtual Environment and Package Manager
This project uses pyenv ( https://github.com/pyenv/pyenv ) for virtual environments and poetry ( https://python-poetry.org/ ) for package management.

There are many other ways to set up a virtual environment. Here are instructions for using pyenv:
```
pyenv versions   # see what's already installed -- is 3.10.x there?
pyenv install 3.10.5  # install it if it's not (otherwise skip this step)
pyenv local 3.10.5   # set this version for your local environment
```
After that, you can set use poetry to install dependencies into this virtual environment:
```
poetry install
```

## Resource dependencies
The `Anatomical Therapeutic Chemical Classification` ontology was downloaded from:
```https://data.bioontology.org/ontologies/ATC/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv```
The ATC ontology is used to group related drugs by drug therapeutic drug class.

Here are its terms of use:
```https://www.bioontology.org/terms/```

## Data -- Drug reviews

I'm using the drug_reviews dataset, available here:
https://huggingface.co/datasets/lewtun/drug-reviews

It can be cloned to your local environment as follows.
```git lfs install
git clone https://huggingface.co/datasets/lewtun/drug-reviews
```

### Sample Example Record from drug review corpus, filtered for condition="High Cholesterol", with annotation
Note the ```<C>``` brackets that are inserted into the 'annotated review' below which mark the boundaries where complaints begin and end.
```commandline

row_id:97673
drug_name: Simvastatin
condition: High Cholesterol
review: """The side effects of this medication are terrible. The dizziness, headache, and not being able to understand what was going on, felt like I was in a cloud. """
rating: 1
useful_count: 68

annotated_review:"""The side effects of this medication are terrible. The <c>dizziness, headache, and not being able to understand what was going on</c>, felt like I was in a cloud. """
annotator_assigned_credibility: High
```


## Usage
TBD


