import json
import re

def parse_to_dict(raw_data):
    clean_text = re.sub(r'```json|```', '', raw_data).strip()
    return json.loads(clean_text)