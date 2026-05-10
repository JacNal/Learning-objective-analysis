from functools import lru_cache
from pathlib import Path

from rdflib import Graph, Literal


GRAPH_PATH = Path(__file__).resolve().parent.parent / "data" / "verbs.ttl"


@lru_cache
def load_graph() -> Graph:
    graph = Graph()
    graph.parse(GRAPH_PATH, format="turtle")
    return graph


def lookup_verb(lemma: str) -> dict:
    graph = load_graph()
    normalized_lemma = lemma.lower().strip()

    main_query = """
    PREFIX loa: <http://127.0.0.1/learning-objective-analysis#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?entry ?type ?measurable ?bloomLabel ?bloomRank
    WHERE {
        ?entry loa:lemma ?lemma ;
               rdf:type ?type ;
               loa:measurable ?measurable .

        OPTIONAL {
            ?entry loa:belongsToBloomLevel ?bloomLevel .
            ?bloomLevel loa:label ?bloomLabel ;
                        loa:rank ?bloomRank .
        }
    }
    LIMIT 1
    """

    results = list(
        graph.query(
            main_query,
            initBindings={
                "lemma": Literal(normalized_lemma),
            },
        )
    )

    if not results:
        return {
            "known": False,
            "type": "unknown",
            "measurable": None,
            "bloom_category": "unknown",
            "bloom_rank": None,
            "replacement_suggestions": [],
        }

    entry, rdf_type, measurable, bloom_label, bloom_rank = results[0]

    replacement_suggestions = get_replacement_suggestions(entry)

    return {
        "known": True,
        "type": local_name(str(rdf_type)),
        "measurable": bool(measurable.toPython()),
        "bloom_category": str(bloom_label) if bloom_label else "unclear",
        "bloom_rank": int(bloom_rank.toPython()) if bloom_rank else None,
        "replacement_suggestions": replacement_suggestions,
    }


def get_replacement_suggestions(entry) -> list[dict]:
    graph = load_graph()

    replacement_query = """
    PREFIX loa: <http://127.0.0.1/learning-objective-analysis#>

    SELECT ?replacementLemma ?bloomLabel ?bloomRank
    WHERE {
        ?entry loa:replacementVerb ?replacement .
        ?replacement loa:lemma ?replacementLemma ;
                     loa:belongsToBloomLevel ?bloomLevel .
        ?bloomLevel loa:label ?bloomLabel ;
                    loa:rank ?bloomRank .
    }
    ORDER BY ?bloomRank ?replacementLemma
    """

    results = graph.query(
        replacement_query,
        initBindings={
            "entry": entry,
        },
    )

    return [
        {
            "verb": str(replacement_lemma),
            "bloom_category": str(bloom_label),
            "bloom_rank": int(bloom_rank.toPython()),
        }
        for replacement_lemma, bloom_label, bloom_rank in results
    ]


def local_name(uri: str) -> str:
    if "#" in uri:
        return uri.rsplit("#", 1)[1]

    return uri.rsplit("/", 1)[-1]