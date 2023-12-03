import logging

from utils_devices import *
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def present_measurement(binding: dict[str, str], historical: bool = False):
    print("Receving data:",binding)
    # if historical:
    #     print(
    #         f"[HISTORICAL] Temperature was {binding['temperature']} units at {binding['timestamp'][1:-1]}",
    #         flush=True,
    #     )
    # else:
    #     print(
    #         f"[NEW!] Live temperature is {binding['temperature']} units at {binding['timestamp'][1:-1]}",
    #         flush=True,
    #     )


def handle_react_measurements(bindings):
    print()
    for binding in bindings:
        present_measurement(binding)
    return []


def start_ui_kb(kb_id, kb_name, kb_description, ke_endpoint):
    register_knowledge_base(kb_id, kb_name, kb_description, ke_endpoint)
    react_measurements_ki = register_react_knowledge_interaction(
        """
            ?sensor rdf:type saref:Sensor .
            ?measurement saref:measurementMadeBy ?sensor .
            ?measurement saref:isMeasuredIn saref:TemperatureUnit .
            ?measurement saref:hasValue ?temperature .
            ?measurement saref:hasTimestamp ?timestamp .
        """,
        None,
        "react-measurements",
        kb_id,
        ke_endpoint,
        {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "saref": "https://saref.etsi.org/core/",
        },
    )

    kb_id2 = kb_id+str(2)
    register_knowledge_base(kb_id2, kb_name, kb_description, ke_endpoint)
    
    react_measurements_ki2 = register_react_knowledge_interaction(
        """
            ?esa rdf:type saref:Device .
            ?esa saref:isUsedFor ?commodity .
            ?commodity rdf:type saref:Electricity .
            ?esa saref:makesMeasurement ?monitoring_of_power_consumption .
            ?monitoring_of_power_consumption saref:relatesToProperty ?power .
            ?power rdf:type saref:Power .
            ?monitoring_of_power_consumption saref:isMeasuredIn ?unit .
            ?monitoring_of_power_consumption saref:hasValue ?value .
        """,
        None,
        "react-measurements",
        kb_id2,
        ke_endpoint,
        {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "saref": "https://saref.etsi.org/core/",
        },
    )
    my_start_handle_loop(
        {
            react_measurements_ki2: handle_react_measurements,
            react_measurements_ki: handle_react_measurements,
        },
        [kb_id,kb_id2],
        ke_endpoint,
    )


if __name__ == "__main__":
    add_sigterm_hook()

    import time

    # logger.info(
    #     "sleeping a bit, so that there are some historical measurements that we can demonstrate to show"
    # )
    time.sleep(1)

    start_ui_kb(
        "http://example.org/ui"+str(random.randint(0,10000)),
        "UI",
        "UI for measurement",
        #"http://knowledge-engine:8280/rest/",
        "http://150.65.230.93:8280/rest/",
    )
