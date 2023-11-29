import datetime
import time
import random
import logging

from utils_devices import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def present_measurement(binding: dict[str, str], historical: bool = False):
    if historical:
        print(
            f"[HISTORICAL] Temperature was {binding['temperature']} units at {binding['timestamp'][1:-1]}",
            flush=True,
        )
    else:
        print(
            f"[NEW!] Live temperature is {binding['temperature']} units at {binding['timestamp'][1:-1]}",
            flush=True,
        )

def handle_react_measurements(bindings):
    print("Triggering handle_react_measurements")
    for binding in bindings:
        present_measurement(binding)

    KB_DATA = [{
                    "sensor": "<https://example.org/sensor/askingsensor>",
                    "measurement": f"<https://example.org/sensor/1/measurement/{56789}>",
                    "temperature": f"{123456}",
                    "timestamp": f'"{datetime.datetime.now().isoformat()}"',
                }]
    data = match_bindings(
            bindings,
            KB_DATA,
        )
    return data


def start_anwer_kb(kb_id, kb_name, kb_description, ke_endpoint):
    register_knowledge_base(kb_id, kb_name, kb_description, ke_endpoint)
    ki_id = register_answer_knowledge_interaction(
    #ki_id = register_post_knowledge_interaction(
        """
            ?sensor rdf:type saref:Sensor .
            ?measurement saref:measurementMadeBy ?sensor .
            ?measurement saref:isMeasuredIn saref:TemperatureUnit .
            ?measurement saref:hasValue ?temperature .
            ?measurement saref:hasTimestamp ?timestamp .
        """,
        "post-measurements",
        kb_id,
        ke_endpoint,
        {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "saref": "https://saref.etsi.org/core/",
        },
    )

    start_handle_loop(
        {
            ki_id: handle_react_measurements,
        },
        kb_id,
        ke_endpoint,
    )


if __name__ == "__main__":
    add_sigterm_hook()

    start_anwer_kb(
        "http://example.org/answer" +  str(random.random()),
        "answer",
        "A sample answer",
        #"http://localhost:8280/rest/",
        "http://150.65.230.93:8280/rest/",
    )
