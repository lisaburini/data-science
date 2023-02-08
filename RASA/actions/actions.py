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

# Action to retrive information about the status of a report
class GetStatusFromDB(Action):
    def name(self) -> Text:
        return "check_status_db"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict):

        dispatcher.utter_message("Sto per verificare i dati nel database!")

        report_id=tracker.get_slot('report_id')
        query = 'SELECT Stato FROM Segnalazioni WHERE ID=%s'

        cursor.execute(query,(report_id,))
        result = cursor.fetchall()
        if len(result) == 0:
            dispatcher.utter_message("Non esiste alcuna segnalazione con questo ID!")
        else:
            dispatcher.utter_message(text=f"La segnalazione numero {report_id} è in questo stato: {result[0][0]}")

        return []