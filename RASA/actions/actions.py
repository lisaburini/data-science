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
from datetime import date
import re
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
            try:
                query = 'SELECT * FROM Segnalazioni WHERE ID=%s'

                cursor.execute(query,(report_id,))
                result = cursor.fetchall()

                if len(result) == 0:
                    dispatcher.utter_message("Non esiste alcuna segnalazione con questo ID!")
                    return [SlotSet("report_id", None)]
                else:
                    if(str(result[0][8]) == 'in coda'):
                        dispatcher.utter_message(text=f"La segnalazione numero {report_id} del giorno {result[0][1]}, con oggetto '{result[0][2]}' presso '{result[0][3]}' è in questo stato: {result[0][8]}.")
                        dispatcher.utter_message(text=f"Ci dispiace non aver ancora potuto prendere in considerazione questa segnalazione. Stiamo facendo il possibile.")
                        return [SlotSet("report_id", None)]
                    elif(str(result[0][8]) == 'in corso'):
                        dispatcher.utter_message(text=f"La segnalazione numero {report_id} del giorno {result[0][1]}, con oggetto '{result[0][2]}' presso '{result[0][3]}' è in questo stato: {result[0][8]}.")
                        dispatcher.utter_message(text=f"Il problema è stato preso in carico in data {result[0][9]}, i nostri operai stanno lavorando per risolverlo il prima possibile.")
                        return [SlotSet("report_id", None)]
                    elif(str(result[0][8]) == 'espletata'):
                        dispatcher.utter_message(text=f"La segnalazione numero {report_id} del giorno {result[0][1]}, con oggetto '{result[0][2]}' presso '{result[0][3]}' è in questo stato: {result[0][8]}.")
                        dispatcher.utter_message(text=f"Siamo felici di informarla che i problemi evidenziati nella segnalazione {report_id} sono stati risolti. L'intervento è stato iniziato in data {result[0][9]} ed è stato concluso in data {result[0][10]}.")
                        return [SlotSet("report_id", None)]
                
                return [SlotSet("report_id", None)]

            except:
                dispatcher.utter_message(text=f"Si è verificato un errore. Non siamo riusciti a reperire le informazioni per la segnalazione numero {report_id}")
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

        # intent = tracker.latest_message['intent'].get('name')
        # intent = tracker.get_intent_of_latest_message(self)
        #dispatcher.utter_message(text=f"intent={intent}")

        # dispatcher.utter_message(text=f"L'ufficio scelto è quello relativo a: {office}")
        if len(result) == 0:
            dispatcher.utter_message("Abbiamo riscontrato un problema nel reperire le informazioni. Ci scusiamo e le chiediamo di riprovare più tardi.")
        else:
            dispatcher.utter_message(text=f"L'ufficio di riferimento per l'area {office} si trova in {result[0][9]} ed è aperto al pubblico nei giorni {result[0][10]}, nei seguenti orari: {result[0][11]}.")
        # return [SlotSet("office", None)]
        return []
        

# Action to retrive information about a particular office
class GetSpecificOfficeInfo(Action):
    def name(self) -> Text:
        return "get_specific_office_info"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict):

        office=tracker.get_slot('specific_area')
        office = str(office)
        office = office.title()

        if(office=='Verde'):
            office = 'Verde Pubblico'
        if(office=='Illuminazione'):
            office = 'Pubblica Illuminazione'        

        if(office=='Viabilita'):
            office = 'Viabilità'
        if(office=='Idraulica'):
            office = 'Termoidraulica'

        # query = 'SELECT Stato FROM Segnalazioni WHERE ID=%s'
        query = 'SELECT * FROM Impiegato WHERE Settore=%s'

        cursor.execute(query,(office,))
        result = cursor.fetchall()

        if len(result) == 0:
            dispatcher.utter_message("L'area di riferimento da lei specificata non è corretta, la preghiamo di riprovare.")
        else:
            dispatcher.utter_message(text=f"L'ufficio di riferimento per l'area {office} si trova in {result[0][9]} ed è aperto al pubblico nei giorni {result[0][10]}, nei seguenti orari: {result[0][11]}.")
        
        # return [SlotSet("specific_area", None)]
        return [SlotSet("office", office)]
    

# Action to retrive information to speak with an operator
class GetEmployeesInfo(Action):
    def name(self) -> Text:
        return "get_employees_info"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict):

        # employee_area=tracker.get_slot('employee_area')
        employee_area=tracker.get_slot('office')
        query = 'SELECT * FROM Impiegato WHERE Settore=%s'

        cursor.execute(query,(employee_area,))
        result = cursor.fetchall()

        # dispatcher.utter_message(text=f"L'ufficio scelto è quello relativo a: {employee_area}")

        if len(result) == 0:
            dispatcher.utter_message("Abbiamo riscontrato un problema nel reperire le informazioni. Ci scusiamo e le chiediamo di riprovare più tardi.")
        else:
            dispatcher.utter_message(text=f"La persona di riferimento per l'ufficio {employee_area} è {result[0][1]} {result[0][2]} e può essere contattata attraverso il numero {result[0][7]} oppure tramite l'email {result[0][8]}.")
        
        # return [SlotSet("office", None)]
        return []


class InsertReportInDB(Action):
    def name(self) -> Text:
        return "submit_report"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict):

        
        today = date.today()
        description =tracker.get_slot('description')
        location = tracker.get_slot('location')
        full_name =tracker.get_slot('full_name')
        phone_number =tracker.get_slot('phone_number')
        email = tracker.get_slot('email')
        tool = 'Chatbot'
        status = 'in coda'

        query = 'INSERT INTO segnalazioni (DataSegnalazione, Oggetto, Località, Segnalatore, TelefonoSegnalatore, EmailSegnalatore, MezzoSegnalazione, Stato) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);'
  
        try:
            cursor.execute(query, (today,description,location,full_name,phone_number,email,tool,status))
            mydb.commit()

            # get id of last report inserted
            query = 'SELECT ID FROM Segnalazioni ORDER BY ID DESC LIMIT 1'
            cursor.execute(query)
            id = cursor.fetchall()

            dispatcher.utter_message(text=f"La sua segnalazione è stata registrata con successo. L'ID di riferimento per la sua segnalazione è {id[0][0]}")
        except:
            dispatcher.utter_message(text="Si è verificato un errore")

        return [SlotSet("description", None), SlotSet("location", None)]


class InsertSuggestionInDB(Action):
    def name(self) -> Text:
        return "submit_suggestion"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict):
       
        today = date.today()
        suggestion =tracker.get_slot('suggestion')
        full_name =tracker.get_slot('full_name')
        phone_number =tracker.get_slot('phone_number')
        email = tracker.get_slot('email')
        tool_used = 'Chatbot'

        if(suggestion=='NULL' and full_name=='NULL' and phone_number=='NULL' and email=='NULL'):
            dispatcher.utter_message(text="La chat è terminata")
            return []
        else:
            query = 'INSERT INTO raccoltaconsigli (DescrizioneConsiglio, Proponente, TelefonoProponente, EmailProponente, DataProposta, MezzoProposta) VALUES (%s,%s,%s,%s,%s,%s);'
            try:
                cursor.execute(query, (suggestion,full_name,phone_number,email,today,tool_used))
                mydb.commit()
                dispatcher.utter_message(text="Grazie, il suo suggerimento è stato registrato con successo")
                dispatcher.utter_message(text="La chat è terminata")
            except:
                dispatcher.utter_message(text="Si è verificato un errore")
            return []


class ValidateInsertReportForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_insert_info_in_report"
    def validate_email(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate email value."""
        # regex = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

        # if re.match(regex, slot_value):
        if (re.fullmatch(regex, slot_value)):
            # validation succeeded, set the value of the "email" slot to value
            return {"email": slot_value}
        else:
            # validation failed, set this slot to None so that the
            # user will be asked for the slot again
            dispatcher.utter_message(text=f"L'email inserita non ha una formattazione valida. Si prega di riprovare.")
            return {"email": None}


# Action to retrive information to speak with an operator
class GetIntentsSuggestion(Action):
    def name(self) -> Text:
        return "fill_slot"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict):

        confirm_button=tracker.get_slot('confirm_button')
        # dispatcher.utter_message(text=f"è partita l'azione dopo il clic dei bottoni e il botton scelto è {confirm_button}")

        if (confirm_button == 'Noo'):
            return [SlotSet("suggestion", 'NULL'), SlotSet("full_name", 'NULL'), SlotSet("phone_number", 'NULL'), SlotSet("email", 'NULL')]
        
        else: 
            return []

        # dispatcher.utter_message(text=f"L'ufficio scelto è quello relativo a: {employee_area}")
        # return [SlotSet("office", None)]

class ValidateInsertSuggestionForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_insert_suggestion"
    def validate_email(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domai
        : DomainDict,
    ) -> Dict[Text, Any]:
        """Validate email value."""
        # regex = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

        
        # if re.match(regex, slot_value):
        if (re.fullmatch(regex, slot_value) or slot_value=='NULL'):
            # validation succeeded, set the value of the "email" slot to value
            return {"email": slot_value}
        else:
            # validation failed, set this slot to None so that the
            # user will be asked for the slot again
            dispatcher.utter_message(text=f"L'email inserita non ha una formattazione valida. Si prega di riprovare.")
            return {"email": None}