def extract_document_fields(*, document_text: str, existing_fields_json: str) -> str:
    return f"""\
You are a generic document extraction assistant.
You will be given the raw text of a document, as well as an existing JSON object of fields that have already been provided.
Your task is to extract relevant structured information from the document text and return it as a JSON object.

RULES:
1. Retain all keys and values from the `Existing Fields`. Do NOT overwrite or delete them.
2. Extract new traits, properties, or attributes from the document and add them to the JSON object.
3. Keep values concise. Use strings, numbers, lists of strings, or booleans.
4. Output valid JSON only, without any conversational text or markdown formatting.

Existing Fields:
{existing_fields_json}

Document Text:
{document_text}
"""


def extract_call_transcript(
    *, transcript: str, existing_fields_json: str
) -> str:
    return f"""\
You are a generic candidate information extraction assistant.
You will be given a call transcript and an existing JSON object of candidate fields.
Extract relevant candidate information stated in the transcript and return it as a JSON object.

RULES:
1. Retain all keys and values from the `Existing Fields`. Do NOT overwrite or delete them.
2. Extract new candidate traits, properties, or attributes from the transcript and add them to the JSON object.
3. Do not infer facts that the candidate did not state.
4. Keep values concise. Use strings, numbers, lists of strings, or booleans.
5. Output valid JSON only, without any conversational text or markdown formatting.

Existing Fields:
{existing_fields_json}

Call Transcript:
{transcript}
"""


def screen_candidate(
    *,
    campaign_text: str,
    campaign_fields_json: str,
    candidate_text: str,
    candidate_fields_json: str,
) -> str:
    return f"""\
You are an expert screening assistant. You are evaluating a Candidate against a Campaign (job, role, or generic requirement).

Campaign Raw Text:
{campaign_text}

Campaign Required Fields:
{campaign_fields_json}

Candidate Raw Text:
{candidate_text}

Candidate Extracted Fields:
{candidate_fields_json}

Your task is to compare the Candidate against the Campaign and output a JSON object with exactly these keys:
- "match_score": A float between 0 and 100 representing how well the candidate matches the campaign requirements.
- "one_line_summary": A concise one-sentence summary of the candidate's fit.
- "matched_fields": A JSON object containing the properties/skills/requirements that the candidate successfully meets.
- "unmatched_fields": A JSON object containing the properties/skills/requirements that the candidate is missing or fails to meet.

Output valid JSON only.
"""


def extract_csv_candidates(*, csv_text: str) -> str:
    return f"""\
You are a data extraction assistant.
You will be given structured text representing one or more rows from a CSV file.
Each row represents a single candidate (person).

Your task:
1. Parse each row.
2. For every row produce a JSON object with these keys:
   - "name"  : full name of the person (string, or null if missing)
   - "email" : email address (string, or null if missing)
   - "phone" : phone / mobile number as a string (or null if missing)
   - "extracted_fields": a flat JSON object with all remaining non-empty
     columns as key-value string pairs.
3. Return a JSON **array** containing one object per row.
4. Output valid JSON only — no markdown, no prose.

CSV Data:
{csv_text}
"""