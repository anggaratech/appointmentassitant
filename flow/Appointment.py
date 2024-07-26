from. import Base_Flow
from config.settings import settings
import requests
import uuid
import pandas as pd

import re
import openai
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage

class Appointment(Base_Flow):

    function_middleware = [{
        "name": "appointment_management",
        "description": """
        This function will be used when the user discusses or requests an appointment, regardless of the topic, such as scheduling an appointment, cancellation, updating, or checking availability.
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": """Date will schedule a meeting. eg : '2024-07-20'""",
                },
                "start_time": {
                    "type": "string",
                    "description": """Start time of the meeting. eg: '10:00:00'""",
                },
                "end_time": {
                    "type": "string",
                    "description": """End time of the meeting. eg: '11:00:00'""",
                },
            },
            "required": ["date", "start_time", "end_time"],
        },
    }
    ]

    def __init__(self,wa_id,wa_name, sentence):

        super().__init__(wa_id=wa_id,wa_name=wa_name,function_middleware=self.function_middleware,sentence=sentence)

    async def appointment_management(self,date, start_time, end_time):

        chat_completion = ChatOpenAI(
            openai_api_key=settings.OPENAI_KEY,
            temperature=0.25,
            model="gpt-4-0125-preview"
        )
        prompt = f"""
        You're intent detector from a user inquiry from user input base on this intent knowledge about user intent.
        user_input: \"{self.sentence}\" 
        can you analyze the user intent? 
        Is it related to these categories  CreateAppointment, UpdateAppointment, or CancelAppointment? if note related response with None.
        Conclude in this format, Answer in this format: 
        The user falls under the category of \"categories\". Because of \"your reasoning\".
        
        """
        try:
            ai_response = chat_completion([SystemMessage(content=prompt)])
            response = str(ai_response.content)
            print(response)

            if 'CreateAppointment' in response:
                result = await self.create_appointment(date, start_time, end_time)
                return result
            elif 'CancelAppointment' in response:
                result = await self.cancel_appointment(date, start_time, end_time)
                return result
            elif 'UpdateAppointment' in response:
                result = await self.create_appointment(date, start_time, end_time)
                return result
        except Exception as e:
            print(e)

    async def validate_new_data(self, df, new_data):
        return not ((df['Date'] == new_data['Date']) &
                    (df['StartTime'] == new_data['StartTime']) &
                    (df['EndTime'] == new_data['EndTime'])).any()


    async def create_appointment(self, date, start_time, end_time):
        appointment = {
            "PhoneNumber": self.wa_id,
            "Name": self.wa_name,
            "Date": date,
            "StartTime": start_time,
            "EndTime": end_time,
        }
        if date and start_time and end_time:
            try:
                df_appointment = pd.read_csv("data/appointments.csv")

                if not await self.validate_new_data(df_appointment, appointment):
                    return f"Sorry {self.wa_name}, for {date} {start_time} {end_time} already booked, we have no slot for that time"
                elif int(self.wa_id) in df_appointment['PhoneNumber'].tolist():
                    return f"Sorry {self.wa_name}, you already have scheduled appointment before. will you cancel the scheduled ?"
                else:
                    new_appointment_df = pd.DataFrame([appointment])
                    df_appointment = pd.concat([df_appointment, new_appointment_df], ignore_index=True)
                    df_appointment.to_csv("data/appointments.csv", index=False)
                    return f"{self.wa_name},your appointment on {date} from {start_time} to {end_time} is confirmed. Looking forward to assisting you with your project!"
            except Exception as e:
                print(e)
                return "Please ensure that you have entered all the required data. Thank you."
        else:
            return "Apologies, you have not filled in all the required information!"


    async def cancel_appointment(self, date, star_time, end_time):
        df_appointment = pd.read_csv("data/appointments.csv")
        try:
            indices_to_drop = df_appointment[df_appointment['Name'] == self.wa_name].index
            df_appointment = df_appointment.drop(index=indices_to_drop)
            df_appointment.to_csv("data/appointments.csv", index=False)
            return f"{self.wa_name},your appointment at {date} {star_time} {end_time} is Canceled"
        except:
            return "Sorry, we have problem now. Please try again later"