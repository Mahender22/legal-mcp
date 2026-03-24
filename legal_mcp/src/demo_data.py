"""Demo mode data — pre-cached results from landmark US Supreme Court cases.

Allows users to try LegalMCP without any API keys by setting LEGAL_MCP_DEMO=true.
"""

# Curated set of famous cases spanning different legal areas
DEMO_CASES = [
    {
        "id": 2812209,
        "caseName": "Carpenter v. United States",
        "court": "scotus",
        "dateFiled": "2018-06-22",
        "citation": ["585 U.S. 296"],
        "snippet": "The Government's acquisition of cell-site location information (CSLI) "
                   "constitutes a search under the Fourth Amendment, requiring a warrant "
                   "supported by probable cause.",
        "cluster_id": 2812209,
        "absolute_url": "/opinion/2812209/carpenter-v-united-states/",
    },
    {
        "id": 98675,
        "caseName": "Brown v. Board of Education",
        "court": "scotus",
        "dateFiled": "1954-05-17",
        "citation": ["347 U.S. 483"],
        "snippet": "Segregation of children in public schools solely on the basis of race "
                   "deprives children of the minority group of equal educational opportunities, "
                   "even though the physical facilities may be equal.",
        "cluster_id": 98675,
        "absolute_url": "/opinion/98675/brown-v-board-of-education/",
    },
    {
        "id": 107252,
        "caseName": "Miranda v. Arizona",
        "court": "scotus",
        "dateFiled": "1966-06-13",
        "citation": ["384 U.S. 436"],
        "snippet": "The prosecution may not use statements stemming from custodial interrogation "
                   "of the defendant unless it demonstrates the use of procedural safeguards "
                   "effective to secure the privilege against self-incrimination.",
        "cluster_id": 107252,
        "absolute_url": "/opinion/107252/miranda-v-arizona/",
    },
    {
        "id": 96405,
        "caseName": "Marbury v. Madison",
        "court": "scotus",
        "dateFiled": "1803-02-24",
        "citation": ["5 U.S. 137"],
        "snippet": "It is emphatically the province and duty of the Judicial Department to say "
                   "what the law is. A law repugnant to the Constitution is void.",
        "cluster_id": 96405,
        "absolute_url": "/opinion/96405/marbury-v-madison/",
    },
    {
        "id": 2700542,
        "caseName": "Obergefell v. Hodges",
        "court": "scotus",
        "dateFiled": "2015-06-26",
        "citation": ["576 U.S. 644"],
        "snippet": "The right to marry is a fundamental right inherent in the liberty of the person, "
                   "and under the Due Process and Equal Protection Clauses of the Fourteenth Amendment, "
                   "same-sex couples may not be deprived of that right.",
        "cluster_id": 2700542,
        "absolute_url": "/opinion/2700542/obergefell-v-hodges/",
    },
    {
        "id": 108713,
        "caseName": "Roe v. Wade",
        "court": "scotus",
        "dateFiled": "1973-01-22",
        "citation": ["410 U.S. 113"],
        "snippet": "The right of personal privacy includes the abortion decision, but this right "
                   "is not unqualified and must be considered against important state interests.",
        "cluster_id": 108713,
        "absolute_url": "/opinion/108713/roe-v-wade/",
    },
    {
        "id": 96282,
        "caseName": "Gideon v. Wainwright",
        "court": "scotus",
        "dateFiled": "1963-03-18",
        "citation": ["372 U.S. 335"],
        "snippet": "The right of an indigent defendant in a criminal trial to have the assistance "
                   "of counsel is a fundamental right essential to a fair trial under the Sixth Amendment.",
        "cluster_id": 96282,
        "absolute_url": "/opinion/96282/gideon-v-wainwright/",
    },
    {
        "id": 2627055,
        "caseName": "Alice Corp. v. CLS Bank International",
        "court": "scotus",
        "dateFiled": "2014-06-19",
        "citation": ["573 U.S. 208"],
        "snippet": "Claims merely requiring generic computer implementation of abstract ideas "
                   "are not patent eligible under 35 U.S.C. Section 101.",
        "cluster_id": 2627055,
        "absolute_url": "/opinion/2627055/alice-corp-v-cls-bank-international/",
    },
    {
        "id": 100247,
        "caseName": "New York Times Co. v. Sullivan",
        "court": "scotus",
        "dateFiled": "1964-03-09",
        "citation": ["376 U.S. 254"],
        "snippet": "A public official may not recover damages for a defamatory falsehood relating "
                   "to official conduct unless actual malice — knowledge of falsity or reckless "
                   "disregard for the truth — is shown.",
        "cluster_id": 100247,
        "absolute_url": "/opinion/100247/new-york-times-co-v-sullivan/",
    },
    {
        "id": 2812485,
        "caseName": "Dobbs v. Jackson Women's Health Organization",
        "court": "scotus",
        "dateFiled": "2022-06-24",
        "citation": ["597 U.S. 215"],
        "snippet": "The Constitution does not confer a right to abortion; Roe v. Wade and Planned "
                   "Parenthood v. Casey are overruled; the authority to regulate abortion is returned "
                   "to the people and their elected representatives.",
        "cluster_id": 2812485,
        "absolute_url": "/opinion/2812485/dobbs-v-jackson-womens-health-organization/",
    },
]

# Build lookup by ID for quick access
_CASES_BY_ID = {c["id"]: c for c in DEMO_CASES}


def _match_cases(query: str) -> list[dict]:
    """Simple keyword matching against demo cases."""
    query_lower = query.lower()
    scored = []
    for case in DEMO_CASES:
        score = 0
        text = f"{case['caseName']} {case['snippet']}".lower()
        for word in query_lower.split():
            if word in text:
                score += 1
        if score > 0:
            scored.append((score, case))
    scored.sort(key=lambda x: -x[0])
    if scored:
        return [c for _, c in scored]
    # If no matches, return all cases
    return DEMO_CASES


def get_demo_search_results(query: str) -> dict:
    """Return demo search results matching the query."""
    matches = _match_cases(query)
    return {
        "count": len(matches),
        "results": matches,
    }


def get_demo_opinion(opinion_id: int) -> dict:
    """Return a demo opinion by ID."""
    case = _CASES_BY_ID.get(opinion_id, DEMO_CASES[0])
    return {
        "id": case["id"],
        "type": "lead",
        "html_with_citations": f"<p>{case['snippet']}</p>",
        "plain_text": case["snippet"],
        "download_url": f"https://www.courtlistener.com{case['absolute_url']}",
        "cluster": case["cluster_id"],
        "author": None,
        "joined_by": [],
    }


def get_demo_docket(docket_id: int) -> dict:
    """Return a demo docket by ID."""
    case = _CASES_BY_ID.get(docket_id, DEMO_CASES[0])
    return {
        "case_name": case["caseName"],
        "court": case["court"],
        "date_filed": case["dateFiled"],
        "date_terminated": case["dateFiled"],
        "assigned_to_str": "Demo Judge",
        "referred_to_str": None,
        "cause": "Constitutional Law",
        "nature_of_suit": "Civil Rights",
        "jury_demand": "None",
        "docket_number": f"No. {case['id']}-demo",
        "pacer_case_id": None,
        "absolute_url": case["absolute_url"],
    }


def get_demo_citations(opinion_id: int) -> dict:
    """Return demo citations (cases cited by this opinion)."""
    other_cases = [c for c in DEMO_CASES if c["id"] != opinion_id][:5]
    return {
        "count": len(other_cases),
        "results": [
            {
                "citing_opinion": opinion_id,
                "cited_opinion": c["id"],
                "depth": 1,
            }
            for c in other_cases
        ],
    }


def get_demo_cited_by(opinion_id: int) -> dict:
    """Return demo reverse citations (cases that cite this opinion)."""
    other_cases = [c for c in DEMO_CASES if c["id"] != opinion_id][:5]
    return {
        "count": len(other_cases),
        "results": [
            {
                "citing_opinion": c["id"],
                "cited_opinion": opinion_id,
                "depth": 1,
            }
            for c in other_cases
        ],
    }
