import re
from logger import setup_logger

logger = setup_logger(__name__)


def clear_tags(message):
    return re.sub(r"(-? ?\[@?.*\]\(.*?\))|}|{", "", message).strip()


def entry_as_string(entry):
    if entry["role"] == "human":
        return f"Human: {clear_tags(entry['content'])}"
    return f"Assistant: {clear_tags(entry['content'])}"


def history_as_text(history):
    return "\n".join(list(map(entry_as_string, history)))
