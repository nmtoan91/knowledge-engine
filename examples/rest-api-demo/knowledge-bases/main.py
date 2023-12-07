import logging
from MainView import MainView
import random
from utils import *
from datetime import datetime
import time
import threading 
import time
from KnowledgeEngineManager import EnergyUseCase, EnergyUseCaseType
import threading
from concurrent.futures import Future
import atexit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Manager:
    instance = None
    # def __new__(cls):
    #     if not hasattr(cls, 'instance'):
    #         cls.instance = super(SingletonClass, cls).__new__(cls)
    #     return cls.instance
    def __init__(self,kb_id,ke_endpoint ):
        Manager.instance = self
        self.kb_id = kb_id
        self.ke_endpoint = ke_endpoint
        self.mainView = MainView("My tkinter thread", 1000,self)

    def Start(self):
        self.RegisterReacts()
        self.mainView.RunOnMainThread()

    def RegisterReacts(self):
        self.energyCases = {}
        self.energyCases[EnergyUseCaseType.FLEXIBLE_START] =  EnergyUseCase(EnergyUseCaseType.FLEXIBLE_START,self)
        # self.energyCases[EnergyUseCaseType.MONITORING_POWER_CONSUMPTION] =  EnergyUseCase(EnergyUseCaseType.MONITORING_POWER_CONSUMPTION,self)
        self.energyCases[EnergyUseCaseType.LIMITATION_POWER_CONSUMPTION] =  EnergyUseCase(EnergyUseCaseType.LIMITATION_POWER_CONSUMPTION,self)
        # self.energyCases[EnergyUseCaseType.MANAGEMENT_POWER_CONSUMPTION_INCENTIVE_TABLE] =  EnergyUseCase(EnergyUseCaseType.MANAGEMENT_POWER_CONSUMPTION_INCENTIVE_TABLE,self)
        # self.energyCases[EnergyUseCaseType.MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN] =  EnergyUseCase(EnergyUseCaseType.MANAGEMENT_POWER_CONSUMPTION_POWER_PLAN,self)
        self.energyCases[EnergyUseCaseType.MANUAL_OPERATION] =  EnergyUseCase(EnergyUseCaseType.MANUAL_OPERATION,self)

        for key in self.energyCases:
            self.energyCases[key].RegisterKnowledgeBaseReact()
            self.energyCases[key].RegisterKnowledgeBaseAsk()

    def Ask(self,type, structuredData):
        if type in self.energyCases:
            self.energyCases[type].Ask(structuredData)
        else: print("[ERROR HERE]")
    def UnRegister(self):
        for key in self.energyCases:
            self.energyCases[key].UnRegisterKnowledgeBaseReact()
            self.energyCases[key].UnRegisterKnowledgeBaseAsk()

#  def unregister(self):
#         if self.ke_url is None:
#             raise Exception(
#                 "Cannot unregister this KB because no knowledge engine URL is known for this object."
#             )

#         response = requests.delete(
#             f"{self.ke_url}/sc", headers={"Knowledge-Base-Id": self.id}
#         )

#         if not response.ok:
#             raise UnexpectedHttpResponseError(response)


def exit_handler():
    print (f'\n\n\n\n\n My application is ending! {Manager.instance.energyCases} \n\n\n\n\n')
    Manager.instance.UnRegister()

if __name__ == "__main__":
    atexit.register(exit_handler)
    random.seed(datetime.now().timestamp())
    add_sigterm_hook()
    manager = Manager("http://example.org/ui3" + str(random.random()), 
                  "http://150.65.230.93:8280/rest/"    )
    manager.Start()
    

