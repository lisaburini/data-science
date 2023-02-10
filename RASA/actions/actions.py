# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
import mysql.connector as sql
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
#
#

''' 
class ActionHelloWorld(Action):

     def name(self) -> Text:
         return "action_hello_world"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

         dispatcher.utter_message(text="Hello World!")

         return []
'''

# Connection to database 
mydb = sql.connect(
        host="localhost",
        user="chatbot",
        password="chatbotpsw",
        database = "chatbot"
        )
cursor = mydb.cursor()

# Action to validate id

















from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


class ValidateCheckStatusForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_check_status_form"

    @staticmethod
    def report_id_db() -> List[Text]:
        """Database of supported id"""
        query = 'SELECT ID FROM Segnalazioni'
        cursor.execute(query)
        result = cursor.fetchall()
        report_id_list = []
        for row in result:
            report_id_list.append(str(row[0]))
        return report_id_list
  

    def validate_report_id(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        if slot_value in self.report_id_db():
            # validation succeeded, set the value of the report_id slot to value
            return {"report_id": slot_value}
        else:
            # validation failed, set this slot to None so that the
            # user will be asked for the slot again
            # dispatcher.utter_message(text=f"lista id: {report_id_list}")
            if(slot_value == 'stop'):
                return {"report_id": "stop"}
            else:
                dispatcher.utter_message(text=f"L'id inserito non è presente nel nostro database. Si prega di riprovare oppure scrivere 'stop'.")
                return {"report_id": None}



# Action to retrive information about the status of a report
class GetStatusFromDB(Action):
    def name(self) -> Text:
        return "check_status_db"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict):

        report_id=tracker.get_slot('report_id')
        # query = 'SELECT Stato FROM Segnalazioni WHERE ID=%s'

        if(report_id == 'stop'):
            return [SlotSet("report_id", None)]
        else:
            query = 'SELECT * FROM Segnalazioni WHERE ID=%s'

            cursor.execute(query,(report_id,))
            result = cursor.fetchall()
            if len(result) == 0:
                dispatcher.utter_message("Non esiste alcuna segnalazione con questo ID!")
            else:
                if(str(result[0][8]) == 'in coda'):
                    dispatcher.utter_message(text=f"La segnalazione numero {report_id} del giorno {result[0][1]}, con oggetto '{result[0][2]}' presso '{result[0][3]}' è in questo stato: {result[0][8]}.")
                    dispatcher.utter_message(text=f"Ci dispiace non aver ancora potuto prendere in considerazione questa segnalazione. Stiamo facendo il possibile.")
                elif(str(result[0][8]) == 'in corso'):
                    dispatcher.utter_message(text=f"La segnalazione numero {report_id} del giorno {result[0][1]}, con oggetto '{result[0][2]}' presso '{result[0][3]}' è in questo stato: {result[0][8]}.")
                    dispatcher.utter_message(text=f"Il problema è stato preso in carico in data {result[0][9]}, i nostri operai stanno lavorando per risolverlo il prima possibile.")
                elif(str(result[0][8]) == 'espletata'):
                    dispatcher.utter_message(text=f"La segnalazione numero {report_id} del giorno {result[0][1]}, con oggetto '{result[0][2]}' presso '{result[0][3]}' è in questo stato: {result[0][8]}.")
                    dispatcher.utter_message(text=f"Siamo felici di informarla che i problemi evidenziati nella segnalazione {report_id} sono stati risolti. L'intervento è stato iniziato in data {result[0][9]} ed è stato concluso in data {result[0][10]}.")
            return [SlotSet("report_id", None)]

# Action to retrive information about a particular office
class GetOfficeInfo(Action):
    def name(self) -> Text:
        return "get_office_info"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict):


        office=tracker.get_slot('office')
        # query = 'SELECT Stato FROM Segnalazioni WHERE ID=%s'
        query = 'SELECT * FROM Impiegato WHERE Settore=%s'

        cursor.execute(query,(office,))
        result = cursor.fetchall()

        dispatcher.utter_message(text=f"L'ufficio scelto è quello relativo a: {office}")

        if len(result) == 0:
            dispatcher.utter_message("Abbiamo riscontrato un problema nel reperire le informazioni. Ci scusiamo e le chiediamo di riprovare più tardi.")
        else:
            dispatcher.utter_message(text=f"L'ufficio di riferimento per l'area {office} si trova in {result[0][9]} ed è aperto al pubblico nei giorni {result[0][10]}, nei seguenti orari: {result[0][11]}.")
        
        return [SlotSet("office", None)]