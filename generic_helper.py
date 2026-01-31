# Author: Dhaval Patel. Codebasics YouTube Channel

import re

def get_str_from_food_dict(food_dict: dict):
    result = ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])
    return result


def extract_session_id(session_str: str):
    if not session_str:
        return ""
    # Format: .../sessions/SESSION_ID/contexts/...
    match = re.search(r"/sessions/(.*?)/contexts/", session_str)
    if match:
        return match.group(1)
    # Format: .../sessions/SESSION_ID (no contexts, e.g. from payload['session'])
    match = re.search(r"/sessions/(.+)$", session_str)
    if match:
        return match.group(1)
    return ""



if __name__ == "__main__":
    print(get_str_from_food_dict({'burger': 2, 'pizza': 1, 'fries': 3}))