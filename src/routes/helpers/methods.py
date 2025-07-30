import random
from datetime import datetime


def generate_4_digit_pin():
    pin = random.randint(1000, 9999)
    return pin


def workspace_template(creator: str):
    return {
        "workspaceName": "",
        "identify": {
            "workspaceCreateAt": datetime.utcnow(),
            "workspaceModifiedAt": datetime.utcnow(),
            "whoModified": '',
            "whoCreated": creator,
        },
        "kpi": [
            {
                "label": "kpis.dashboard.completion_rate",
                "value": "0%",
                "delta": 0,
            },
            {
                "label": "kpis.dashboard.active_forms",
                "value": "0",
                "delta": 0,
            },
            {
                "label": "kpis.dashboard.responses_today",
                "value": "0",
                "delta": 0,
            },
            {
                "label": "kpis.dashboard.pending_candidates",
                "value": "0",
                "delta": 0,
            },
        ],
        "forms": [],
        "priorities": [],
    }
