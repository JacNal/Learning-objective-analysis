# Learning Objective Analysis API

## Project description
This project implements a small web service that analyses learning objectives based on course descriptions. The system checks whether a learning objective uses quantifiable action verbs, whether the wording is vague and whether the objective is supported by the course description.

The project combines NLP preprocessing, a small RDF knowledge graph inspired by Blooms Taxonomy and an optional LLM-based feedback component using DSPy. The deterministic part of the system does verb extraction, knowledge graph lookup, keyword extraction and content support evaluation. The LLM component then uses this to analysis to generate a short explanation and a suggested rewrite.

## System architecture
The system is implemented as a containerized FastAPI web service.

```text
Client
  |
  v
FastAPI endpoint
  |
  v
spaCy NLP extraction
  |--> action verb extraction
  |--> keyword extraction
  |
  v
RDFLib knowledge graph
  |--> Bloom taxonomy level lookup
  |--> measurable/vague classification
  |--> replacement suggestions
  |
  v
Content support score
  |
  v
LLM feedback
  |
  v
Structured response
```

## Analysis pipeline
For each learning objective, the service performs the following steps:

1. Receives a learning objective and course content as JSON.
2. Uses spaCy to extract action verbs and vague multi-word phrases
3. Looks up detected verb lemmas and phrases in a small RDF knowledge graph.
4. Classifies verbs as measurable, vague or unknown and assigns Bloom levels where possible.
5. Extract keywords from the learning objective and course content.
6. Estimate whether the learning objective is supported by the course content.
7. Uses DSPy and an LLM to generate a short explanation and suggested rewrite.
8. Returns a structured JSON response.

## Tools used

For this project I used: FastAPI for the REST API, Docker for containerization, pytest for unit tests, spaCy for NLP preprocessing, verb extraction, lemmatization and keyword extraction.

I also used RDFLib and SPARQL for the Blooms taxonomy inspired verb knowledge graph, DSPy for the LLM-based explanation and rewriting.

## Running the service

The service can be run without the use of an LLM if you simply do not set up any .env file. An example .env file has been created (.env.example). You have to set up a .env file and use your own API key in order to use the LLM feature of the service.

When the service is running you can either use the endpoints described in the API documentation later or http://127.0.0.1:8000/docs, though the response body is usually pretty long and you might have to scrool a bit to read it all.

### How to run outside of container

#### Set up a venv

First create and activate a virtual environment:
```text
python -m venv .venv-nlp
source .venv-nlp/bin/activate
```
Then install the required dependencies:
```text
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```
#### Use

Now with your dependencies installed and an active venv you can run the api using either 
```text
ENABLE_LLM=false uvicorn app.main:app --reload
```
or 
```text
uvicorn app.main:app --reload
```
The first command disables the use of the LLM for responses in order to get fully reproducible behaviour.

For an easier way to interact with the endpoints and get an overview you can then go to 

http://127.0.0.1:8000/docs

to interact with the endpoints and see some general information

### How to run with Docker

First build the container using the following command inside the project folder:
```text
docker build -t loa .
```
and then run the container using either

#1
```text
docker run --rm -p 8000:8000 loa
```
or 

#2
```text
docker run --rm --env-file .env -p 8000:8000 loa
```
The second command passes your .env file to the docker container such that the LLM can be used. If the container is ran using the first command.

For an easier way to interact with the endpoints and get an overview you can then go to 

http://127.0.0.1:8000/docs

to interact with the endpoints and see some general information

## API documentation

### Base path:
```text
/api/v1
```

### Health check:
```text
GET /api/v1/health
```

An example response could be the following:
```text
{
  "status": "ok",
  "service": "learning-objective-analysis",
  "version": "1.0.1 :)"
}
```

### Analyse one learning objective:
```text
POST /api/v1/analyse
```

A request should be formatted in the same way as the example below:
```text
{
  "learning_objective": "The learning objective",
  "course_content": "The course description"
}
```

A response might look like this. A full response is way longer, so I emptied all the fields, but the general format is the following:
```text
{
  "learning_objective": "The learning objective",
  "detected_verbs": [],
  "issues": [],
  "content_support": {},
  "llm_used": false,
  "explanation": "...",
  "suggested_rewrite": "..." or null
}
```

### Analyse multiple learning objectives:
```text
POST /api/v1/multi
```

Here is an example with the request format:
```text
{
  "course_content": "The course description",
  "learning_objectives": [
    "Learning objective #1",
    "Learning objective #2"
  ]
}
```

The response is just multiple of the single learning objective responses.

### Look up a verb in the knowledge graph:
```text
GET /api/v1/verbs/{verb}
```

Here is an example:
```text
GET /api/v1/verbs/understand
```

## Dataset

The evaluation dataset is stored in:

```text
data/dtu_examples_test.jsonl
```

The dataset consists of manually curated examples based on public DTU course descriptions and learning objectives. Each example contains source course number, course title, url, learning objective, course content, expected detected verb lemmas, expected issue types, expected content-support status.

Some examples intentionally pair a real learning objective with course content from another courseto test whether the system can detect unsupported learning objectives.

## Evaluation

To evaluate I created a script that can be run using 
```text
ENABLE_LLM=false .venv-nlp/bin/python scripts/evaluate.py
```
Evaluation was run on `data/dtu_examples_test.jsonl` with LLM disabled giving me the following results:
```text
Examples: 12
Verb lemma accuracy: 0.92
Issue detection accuracy: 0.92
Content-support accuracy: 0.50
```
The verb extraction component performs best because it uses spaCy lemmatization combined with the Bloom-inspired knowledge graph. Issue detection and content-support scoring are weaker because they rely on heuristic keyword and noun-chunk overlap. This is especially bad when the course content and learning objective are related in concepts but use different terminology/wording.

I also included a bunch of unit tests, that check whether all the API functionalities are working as expected. 
## Limitations

## Tests