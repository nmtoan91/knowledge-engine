import logging
from MainView import MainView
import random
from utils import *

mainView = MainView("My tkinter thread", 1000)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def present_measurement(binding: dict[str, str], historical: bool = False):
    s = "data="
    for key, value in binding.items() :
        s += f"{key}:{value}  "
    print(s)

    # if historical:
    #     print(
    #         f"[HISTORICAL] Temperature was {binding['temperature']} units at {binding['timestamp'][1:-1]}",
    #         flush=True,
    #     )
    # else:
    #     print(
    #         f"[NEW!] ffffff is {binding['temperature']} units at {binding['timestamp'][1:-1]}",
    #         flush=True,
    #     )
    mainView.RevieveData(binding)


def handle_react_measurements(bindings):
    for binding in bindings:
        present_measurement(binding)
    return []


def start_ui_kb(kb_id, kb_name, kb_description, ke_endpoint):
    #Sensor
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

    # start_handle_loop(
    #     {
    #         react_measurements_ki: handle_react_measurements,
    #     },
    #     kb_id,
    #     ke_endpoint,
    # )
    #return
    #Washing machine
    kb_id2 = kb_id+str(2)
    #kb_id2 = kb_id
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

    start_handle_loop(
        {
            react_measurements_ki2: handle_react_measurements,
            react_measurements_ki: handle_react_measurements,
        },
        kb_id,
        ke_endpoint,
    )
    #print("\n\n\n\n\n\n CCCCCCCCCCCCCCCCCCCCCCCCC \n\n\n\n")





if __name__ == "__main__":
    add_sigterm_hook()

    import time

    logger.info(
        "sleeping a bit, so that there are some historical measurements that we can demonstrate to show"
    )
    

    
     
    mainView.start() 
    
    time.sleep(1)
    start_ui_kb(
        "http://example.org/ui3" + str(random.random()) ,
        "UI",
        "UI for measurement",
        "http://150.65.230.93:8280/rest/",
    )