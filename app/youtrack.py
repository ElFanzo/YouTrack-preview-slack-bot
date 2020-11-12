import re
from typing import List, Optional

import requests

# YouTrack API
# https://youtrack.{Your organization domain}/api/openapi.json
URL = "https://youtrack.{Your organization domain}/api/issues/?query=issue%20id:+{}&" \
      "fields=idReadable,summary,description,customFields(name,value(name))"


def get_tasks_names(data: str) -> List[str]:
    """Fetch tasks names like 'SITE-2000' from a message."""
    return re.findall(r"issue\/([A-Z]+-\d+)", data)


def get_task_info(task_name: str) -> Optional[str]:
    """Fetch the task data from YouTrack API."""
    url = URL.format(task_name)
    response = requests.get(url).json()

    if not response or "error" in response:
        return
    task = response[0]

    state = list(filter(lambda x: x["name"] == "State", task["customFields"]))[0]["value"]["name"]
    assignee = list(filter(lambda x: x["name"] == "Assignee", task["customFields"]))[0]["value"]
    data = f"""*{task['idReadable']}*: {task['summary']}\n
*State*: {state}
*Assignee*: {assignee["name"] if assignee else "None"}"""
    if task.get('description'):
        data = f"{data}\n\n{task['description'][:255]}{'...' if len(task['description']) > 255 else ''}"

    return data


def get_previews(message: str) -> List[str]:
    """Get preview for each task in message."""
    return [get_task_info(task_name) for task_name in get_tasks_names(message)]


if __name__ == '__main__':
    print(get_previews("https://youtrack.smena.space/issue/SITE-1990"))
