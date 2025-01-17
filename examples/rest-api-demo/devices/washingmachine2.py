import datetime
import time
import random
import logging

from utils_devices import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_random_temperature(start=15.0, end=20.0):
    assert end > start
    return start + (end - start) * random.random()


def start_sensor_kb(kb_id, kb_name, kb_description, ke_endpoint):
    register_knowledge_base(kb_id, kb_name, kb_description, ke_endpoint)
    ki_id = register_post_knowledge_interaction(
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
        "post-measurements",
        kb_id,
        ke_endpoint,
        {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "saref": "https://saref.etsi.org/core/",
        },
    )

    measurement_counter = 0
    while True:
        now = datetime.datetime.now()
        measurement_counter += 1
        value = generate_random_temperature(12, 26)

        post(
            [
                {
                    "esa": "<https://example.org/washingmachine/1>",
                    "commodity": "<https://example.org/commodity/electric>",
                    "monitoring_of_power_consumption": f"<https://example.org/sensor/1/measurement/{measurement_counter}>",
                    "power": f"<https://example.org/power/123>",
                    "unit": f'"watt"',
                    "value": f"{value}",
                }
            ],
            ki_id,
            kb_id,
            ke_endpoint,
        )
        logger.info(f"published measurement of {value} units at {now.isoformat()}")

        time.sleep(2)


if __name__ == "__main__":
    add_sigterm_hook()

    start_sensor_kb(
        "http://example.org/washingmachine/mc12",
        "Sensor",
        "A temperature sensor",
        "http://150.65.230.93:8280/rest/",
        #"http://localhost:8280/rest/",
    )
