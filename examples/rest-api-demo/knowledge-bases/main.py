import logging
from MainView import MainView
import random
from utils import *
from datetime import datetime
import time
mainView = MainView("My tkinter thread", 1000)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def present_measurement(binding: dict[str, str],requestingKnowledgeBaseId, historical: bool = False):
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
    mainView.RevieveData(binding,requestingKnowledgeBaseId)


def handle_react_measurements(bindings,requestingKnowledgeBaseId):
    now = datetime.now()
    for binding in bindings:
        present_measurement(binding,requestingKnowledgeBaseId)
    print("end receving: ", (datetime.now() - now).seconds,"seconds")
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




import threading 
class KBInThread(threading.Thread):
    def run(self):
        time.sleep(1)
        print('start_ui_kb')
        start_ui_kb(
            "http://example.org/ui3" + str(random.random()) ,
            "UI",
            "UI for measurement",
            "http://150.65.230.93:8280/rest/",
        )

if __name__ == "__main__":
    random.seed(datetime.now().timestamp())
    add_sigterm_hook()

    import time

    isUIOnMainThread = True
    if isUIOnMainThread:
        kbInThread = KBInThread()
        kbInThread.start()
        mainView.RunOnMainThread()
        
    else:
        mainView.start() 
        time.sleep(1)
        start_ui_kb(
            #"http://example.org/ui3" + str(random.random()) ,
            "http://example.org/ui3" + str(random.randint(0,10000)) ,
            "UI",
            "UI for measurement",
            "http://150.65.230.93:8280/rest/",
        )
