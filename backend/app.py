from flask import Flask, request, jsonify
from flask_cors import CORS

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Dict, Optional
# import streamlit as st
import json
from dotenv import load_dotenv
import os
from langchain.memory import ConversationBufferMemory


load_dotenv()

openai_api_key = os.getenv("OPEN_API_KEY")

class FieldUpdate(BaseModel):
    field_name: str
    answer: str

class ResponseStructure(BaseModel):
    inferences: Optional[List[FieldUpdate]] = None
    next_reply: str
    metadata:str

app = Flask(__name__)
CORS(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    chat_history = data.get('chat_history', [])
    current_json = data.get('jsonData', {})

    # Prepare messages for the API call
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for chat in chat_history:
        if chat.lower().startswith('user:'):
            role = "user"
            content = chat.split(': ', 1)[1]  # Remove "User:" from the content
        elif chat.lower().startswith('bot:'):
            role = "assistant"
            content = chat.split(': ', 1)[1]  # Remove "Bot:" from the content
        else:
            # Default role or handle cases where prefix is not recognized
            role = "user"
            content = chat
        
        messages.append({"role": role, "content": content})

    # print(messages)

    

    try:
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",  # or the appropriate model
        #     messages=messages
        # )
        # openai_reply = response.choices[0].message['content']

        # # Mock inference logic (replace with actual LangChain logic)
        # inferences = [
        #     {"field_name": "firstDestination", "answer": "Paris"},
        #     # Add other inferred fields based on your actual LangChain response
        # ]
        current_json, next_reply, options = call_openai_api(messages, flatten_json(current_json))

        return jsonify({
            "current_json": current_json,
            "next_reply": next_reply,
            "options": options
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def call_openai_api(chat_history, current_json):

    model = ChatOpenAI(api_key=openai_api_key, temperature=0)

    # Define the parser
    parser = JsonOutputParser(pydantic_object=ResponseStructure)

    details = {
        "fields": [
            {
                "field_name": "optimizeType",
                "question": "Would you prefer to sequence the list of cities manually, or should we auto-sequence them for you?",
                "options": ["manual", "auto"]
            },
            {
                "field_name": "firstDestination",
                "question": "Where would you like to go first?"
            },
            {
                "field_name": "trip_theme",
                "question": "What is the theme of your trip (e.g., adventure, beach, cultural)?",
                "options": [
                    "romantic",
                    "family-vacation",
                    "eco-tourism",
                    "party",
                    "roadtrip",
                    "remote-work",
                    "business-work",
                    "health and wellness",
                    "spiritual",
                    "lbgtq+",
                    "adventure",
                    "general-tourism-no-theme"
                ]
            },
            {
                "field_name": "destination",
                "question": "Could you provide the list of destinations you plan to visit?",
                "instruction": "this will be a list so even in inference give back a list. if the user updates this then also give the final list in inference as whatever you give will be replaced with previous value"
            },
            {
                "field_name": "traveller_type",
                "question": "What type of traveler are you (e.g., solo, family, friends)?",
                "options": [
                    "solo",
                    "couple",
                    "family-no kids",
                    "family-with kids",
                    "friends"
                ]
            },
            {
                "field_name": "Origin_city",
                "question": "What is your city of origin?"
            },
            {
                "field_name": "budget",
                "question": "How would you describe your budget for this trip?",
                "options": [
                    "on a tight budget",
                    "comfortable spending",
                    "happy to spend for a luxurious vacation"
                ]
            },
            {
                "field_name": "food",
                "question": "Do you have any dietary preferences?",
                "options": [
                    "any",
                    "Middle-eastern",
                    "indian",
                    "asian",
                    "european",
                    "mexican",
                    "vegetarian",
                    "south american",
                    "vegan",
                    "seafood",
                    "fast food",
                    "cafe",
                    "dessert",
                    "healthy",
                    "bar/pub",
                    "barbeque",
                    "pizza"
                ]
            },
            {
                "field_name": "trip_direction",
                "question": "Is your trip one-way or round-trip?",
                "options": ["return", "oneway"]
            },
            {
                "field_name": "time_schedule_onward_trip_time_hour",
                "question": "At what time would you like to depart?",
                "value_option":  ["AM/PM" , "24Hour"],
                "instructions": "user needs to specify if the time is in am or pm or in 24 hour format if you cannot infer this then ask user for clarification"
            },
            {
                "field_name": "time_schedule_onward_trip_time_minute",
                "question": "Minute:"
            },
            {
                "field_name": "time_schedule_onward_trip_date_day_of_month",
                "question": "Day of the month:",
                "options": [1, 31]
            },
            {
                "field_name": "time_schedule_onward_trip_date_month",
                "question": "Month:",
                "options": [1, 12]
            },
            {
                "field_name": "time_schedule_onward_trip_date_year",
                "question": "Year:",
                "options": ["current_year", "next_year"]
            },
            {
                "field_name": "time_schedule_return_trip_time_hour",
                "question": "At what time would you like to depart?",
                "value_option":  ["AM/PM" , "24Hour"],
                "instructions": "user needs to specify if the time is in am or pm or in 24 hour format if you cannot infer this then ask user for clarification"
            },
            {
                "field_name": "time_schedule_return_trip_time_minute",
                "question": "Minute:"
            },
            {
                "field_name": "time_schedule_return_trip_date_day_of_month",
                "question": "Day of the month:",
                "options": [1, 31]
            },
            {
                "field_name": "time_schedule_return_trip_date_month",
                "question": "Month:",
                "options": [1, 12]
            },
            {
                "field_name": "time_schedule_return_trip_date_year",
                "question": "Year:",
                "options": ["current_year", "next_year"]
            },
            {
                "field_name": "time_schedule_duration_value",
                "question": "Duration value:"
            },
            {
                "field_name": "time_schedule_duration_unit",
                "question": "Duration unit:",
                "options": ["week", "month", "days"]
            }
        ]
    }


    query = f"""
            You are a travel assistant chatbot. Your name is Travel.AI, and you are designed to help users plan their trips and provide travel-related information. First, you need to get some information from the user. You will receive the current conversation history and a JSON template with the questions that need to be filled based on user inputs.

            You have to interact with the user as a customer service agent and get them to answer questions in order to fill the question JSON template. Ensure your responses are polite, engaging, and context-aware, using natural language to guide the user through the necessary details. Here are some key points to remember:

            1. Engage in a conversational manner to enhance user retention as a customer service agent would do.
            2. Analyze the chat history carefully before responding and giving inferences (chat history contains chat in the ascending order of time of conversation).
            3. each of your reply should be more than 20 words atleast. (most important)
            4. if you think at any place the user is confused or asking for suggestion then change the chat_mode to "suggestion" and and reply with "Sure I can help you decide"
            5. if user refuses to answer any question then or say no to any question or asks to skip then strictly skip that question for now and move on. you bring that question again later in the conversation in a different way(most important)
            6. also allow updation and deletion of answers.
            7. only give the inferences when you have the answer
            8. do not rely on guess work. only give inferences after analyzing the user's answer
            9. if a user tries to skip a question or says no to a question. strictly move to next unanswered question and if it is the only unanswered question left then give a polite reply and explain how important it is to get that data and try asking the same thing in a different tone and way
            10 if to any question the user says he has not decided yet then go to suggestion mode
            11. in the reason always mention your reason behind the inference and if you are not giving inferences then also state why along with latest user input
            12. if in your next_reply you are asking a particular question with value options then provide the field name of that field in the metadata accurately. (most most important) .   Also for these cases with value options you do not need to provide options in your next_reply itself as i will again be providing that myself. so for these cases just say choose from below options or something like that
 

            Details on each field and how to ask questions: {json.dumps(details, indent=4)}

            Please ensure responses are informative, accurate, and tailored to the user's queries and preferences. Use natural language to engage users and provide a seamless experience throughout their travel planning journey.

            Below are a few examples for you to learn how to do it:

            Example 1:

            bot: Hello! I am here to help you plan your vacation. Let's get started! Where are you planning to go for vacation this time?
            User: Paris.
            {{
                "inferences": [
                    {{"field_name": "destination", "answer": ["Paris]"}}
                ],
                "next_reply": "are you visiting only one city. if there are more than one city you can give me a list of cities you wish to visit",
                "metadata": "none"
            }}

            User: yes I am only going to paris.
            {{
                {{"field_name": "destination", "answer": ["Paris"]}},
                "next_reply": "Do you have a specific theme for your trip, like cultural, romantic, or maybe an adventure?",
                "metadata": "trip_theme"
            }}

            User: I'm planning a wellness and yoga retreat.
            {{
                "inferences": [],
                "next_reply": "It seems like 'wellness and yoga retreat' is not an available option. Could you please choose from the following themes: romantic, family-vacation, eco-tourism, party, roadtrip, remote-work, business-work, health and wellness, spiritual, LGBTQ+, adventure, general-tourism-no-theme?",
                "metadata": "trip_theme"
            }}

            User: Health and wellness sounds good.
            {{
                "inferences": [
                    {{"field_name": "trip_theme", "answer": "health and wellness"}}
                ],
                "next_reply": "Could you provide a list of other destinations you plan to visit after Paris?",
                "metadata": "none"
            }}

            User: Sure, we plan to visit Rome and Barcelona as well.
            {{
                "inferences": [
                    {{"field_name": "destination", "answer": ["Paris", "Rome", "Barcelona"]}}
                ],
                "next_reply": "Do you want to manually sequence the cities you will visit, or should we auto-sequence it?"
            }}

            User: Let's go with the auto-sequencing option.
            {{
                "inferences": [
                    {{"field_name": "optimizeType", "answer": "auto"}}
                ],
                "next_reply": "What is your origin city from where you will leave for vacation?",
                "metadata": "none"
            }}

            User: I am currently living in San Francisco, so it is my origin city.
            {{
                "inferences": [
                    {{"field_name": "Origin_city", "answer": "San Francisco"}}
                ],
                "next_reply": "How would you describe your budget for this trip? Please choose from: 'on a tight budget', 'comfortable spending', 'happy to spend for a luxurious vacation'.",
                "metadata": "budget"
            }}

            User: Can we skip that? Let's talk about my food preferences instead.
            {{
            "inferences": [],
            "next_reply": "Sure! Do you have any dietary preferences or restrictions? Please choose from: 'any', 'Middle-eastern', 'indian', 'asian', 'european', 'mexican', 'vegetarian', 'south american', 'vegan', 'seafood', 'fast food', 'cafe', 'dessert', 'healthy', 'bar/pub', 'barbeque', 'pizza'.",
            "metadata": "food"
            }}

            User: I prefer Asian cuisine.
            {{
            "inferences": [
                {{"field_name": "food", "answer": "asian"}}
            ],
            "next_reply": "Got it! Now, it would really help me to know your budget for this trip to give you the best recommendations. Can you choose from: 'on a tight budget', 'comfortable spending', 'happy to spend for a luxurious vacation'?"
            }}

            User: I'd rather not say.
            {{
            "inferences": [],
            "next_reply": "No worries! Let's try this: Are you looking for budget-friendly options, mid-range comforts, or luxury experiences?",
            "metadata": "budget"
            }}

            User: Mid-range comforts.
            {{
            "inferences": [
                {{"field_name": "budget", "answer": "comfortable spending"}}
            ],
            "next_reply": "Great! Is your trip going to be one-way or a round trip? Please choose from: 'return', 'oneway'.",
            "metadata": "trip_direction"
            }}



            Example 2:

            Bot: Hello! I am here to help you plan your vacation. Let's get started! Where are you planning to go for vacation this time?
            User: Hi, I am not sure where to start. Can you suggest some popular destinations?
            {{
                "inferences": [],
                "next_reply": "Sure! Could you tell me a bit about your preferences? Are you looking for cultural experiences, adventure, relaxation, or something else? also i am changing the mode to sggestion",
                "metadata": "none"
            }}



            Example 3:

            Bot: Hello! I am here to help you plan your vacation. Let's get started! Where are you planning to visit this time for vacation?
            User: You suggest me some.
            {{
            "inferences": [],
            "next_reply": "Sure I can help you decide! Could you tell me a bit about your preferences? Are you looking for cultural experiences, adventure, relaxation, or something else? also i am changing the mode to sggestion",
            "metadata": "none"
            }}

            Remember the above are just some examples for you to learn from. Do not include this data in your inferences; base your output on the conversation in chat history.

            
            know that the above examples contain the entire chat whereas you have to only take the recent chat history and give inference and the next reply or question only in your answer and nothing else.

            your output json should have this structure :

            {{
                "inferences": [],
                "next_reply": "",
                "metadata": "this will contain the field name of the question you are asking in the next_reply if that field has value options to choose from. if you are suggestion or not asking any question from the current json then just state 'none' here",
                "reason": "here you have to give your reasons for whatever inference you gave along with latest user input. example - i am giving inference for destination to be tokyo as the user mentioned tokyo in this latest input ie. 'i wish to to to tokyo' and if you are leaving the inference empty then state why so"
            }}

            just give me this json as output nothing else
            your inferences should be based on latest chat history nd relevent to what is going on here : {chat_history[-5:-1]}
            if the suggestion is going on then give suggestion only and help the user decide. base your suggestion on the questions already answered.

            also you can give inferences even for a one word answer based on the context from the chat_hist0ry

            
            Chat history:
            {chat_history}

            Questions that need to be answered (some of them have been answered; focus on those that are still not answered):
            {json.dumps(current_json, indent=4)}

            remember to chek if before giving inferences if the user has answered or not. see the latest user input in chat history if you want
            also if you cannot match the answer to the value options then ask the user to clarify 

            only when all the questions have been answered say: "thankyou i have all the info i need"

            also you can ask questions in any order you would like

            also do not use any made up data or the data from the examples they were just for you to learn.

            and finally the most important thing: before asking any question analyze the entire chat history for if the question is already answered or not


            be extra careful when asking for date and time. you can club those questions together.
            Also dont ask the user to ask in a given format its your task to convert the time into that format. also if possible infer the minuter from the context and dont ask seperately for it. example 1am means 1 hour and 00 minutes. 
            
            never ask the questions for which a clear answer is already present. only if you wish to clarify it then you can ask

            and when all the questions are answered then say "thankyou i have all in need"

            remember that if the user asks for you to choose any then they are talking about that specific question only. that too you have to confirm with the user.

            """


    # Define the prompt template
    prompt = PromptTemplate(
        template="""Answer the user query.\n{query}\n""",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Create the LLMChain
    chain = prompt | model | parser

    # Prepare the input for the chain
    input_data = {
        "query":query
    }

    # Invoke the chain
    response = chain.invoke({"query":query})

    # Convert response to dictionary
    print(chat_history[-1],"     response:", json.dumps(response, indent=4))
    updated_json = response

    # Update the current JSON with the new answers
    if "inferences" in updated_json and updated_json["inferences"]:
        for update in updated_json["inferences"]:
            if current_json[update["field_name"]] == "destination":
                current_json[update["field_name"]] = list(set(current_json["destination"].append(update["answer"])  ))
            else:
                current_json[update["field_name"]] = update["answer"]

    # if "inferences" in updated_json and updated_json["inferences"]:
    #     for update in updated_json["inferences"]:
    #         field_name = update["field_name"]
    #         answer = update["answer"]
            
    #         if field_name in options_list and answer not in options_list[field_name]:
    #             updated_json["next_reply"] = "Could you clarify?"
    #             break
            
    #         if current_json.get(field_name) == "destination":
    #             current_json[field_name] = list(set(current_json["destination"] + [answer]))
    #         else:
    #             current_json[field_name] = answer

    # print("updated json :", json.dumps(current_json, indent=4))


    return unflatten_json(current_json), updated_json.get("next_reply", ""), get_options(updated_json.get("metadata", ""))
    # return updated_json



def flatten_json(nested_json):
    flat_json = {}

    flat_json["optimizeType"] = nested_json.get("optimizeType", {})
    flat_json["firstDestination"] = nested_json.get("firstDestination", {})
    flat_json["trip_theme"] = nested_json.get("trip_theme", {})
    flat_json["destination"] = nested_json.get("destination", [])
    flat_json["traveller_type"] = nested_json.get("traveller_type", {})
    flat_json["Origin_city"] = nested_json.get("Origin_city", {})
    flat_json["budget"] = nested_json.get("budget", {})
    flat_json["food"] = nested_json.get("food", {})
    flat_json["trip_direction"] = nested_json.get("trip_direction", {})

    time_schedule = nested_json.get("time_schedule", {})
    onward_trip = time_schedule.get("onward_trip", {})
    return_trip = time_schedule.get("return_trip", {})
    duration = time_schedule.get("duration", {})

    flat_json["time_schedule_onward_trip_time_hour"] = onward_trip.get("time", {}).get("hour", {})
    flat_json["time_schedule_onward_trip_time_minute"] = onward_trip.get("time", {}).get("minute", {})
    flat_json["time_schedule_onward_trip_date_day_of_month"] = onward_trip.get("date", {}).get("day_of_month", {})
    flat_json["time_schedule_onward_trip_date_month"] = onward_trip.get("date", {}).get("month", {})
    flat_json["time_schedule_onward_trip_date_year"] = onward_trip.get("date", {}).get("year", {})

    flat_json["time_schedule_return_trip_time_hour"] = return_trip.get("time", {}).get("hour", {})
    flat_json["time_schedule_return_trip_time_minute"] = return_trip.get("time", {}).get("minute", {})
    flat_json["time_schedule_return_trip_date_day_of_month"] = return_trip.get("date", {}).get("day_of_month", {})
    flat_json["time_schedule_return_trip_date_month"] = return_trip.get("date", {}).get("month", {})
    flat_json["time_schedule_return_trip_date_year"] = return_trip.get("date", {}).get("year", {})

    flat_json["time_schedule_duration_value"] = duration.get("value", {})
    flat_json["time_schedule_duration_unit"] = duration.get("unit", {})

    return flat_json


def unflatten_json(flat_json):
    nested_json = {}

    nested_json["optimizeType"] = flat_json.get("optimizeType", {})
    nested_json["firstDestination"] = flat_json.get("firstDestination", {})
    nested_json["trip_theme"] = flat_json.get("trip_theme", {})
    nested_json["destination"] = flat_json.get("destination", [])
    nested_json["traveller_type"] = flat_json.get("traveller_type", {})
    nested_json["Origin_city"] = flat_json.get("Origin_city", {})
    nested_json["budget"] = flat_json.get("budget", {})
    nested_json["food"] = flat_json.get("food", {})
    nested_json["trip_direction"] = flat_json.get("trip_direction", {})

    time_schedule = {}
    onward_trip = {}
    return_trip = {}
    duration = {}

    onward_trip["time"] = {
        "hour": flat_json.get("time_schedule_onward_trip_time_hour", {}),
        "minute": flat_json.get("time_schedule_onward_trip_time_minute", {})
    }
    onward_trip["date"] = {
        "day_of_month": flat_json.get("time_schedule_onward_trip_date_day_of_month", {}),
        "month": flat_json.get("time_schedule_onward_trip_date_month", {}),
        "year": flat_json.get("time_schedule_onward_trip_date_year", {})
    }

    return_trip["time"] = {
        "hour": flat_json.get("time_schedule_return_trip_time_hour", {}),
        "minute": flat_json.get("time_schedule_return_trip_time_minute", {})
    }
    return_trip["date"] = {
        "day_of_month": flat_json.get("time_schedule_return_trip_date_day_of_month", {}),
        "month": flat_json.get("time_schedule_return_trip_date_month", {}),
        "year": flat_json.get("time_schedule_return_trip_date_year", {})
    }

    duration = {
        "value": flat_json.get("time_schedule_duration_value", {}),
        "unit": flat_json.get("time_schedule_duration_unit", {})
    }

    time_schedule["onward_trip"] = onward_trip
    time_schedule["return_trip"] = return_trip
    time_schedule["duration"] = duration

    nested_json["time_schedule"] = time_schedule

    return nested_json


def get_options(field_name):
    options_list = {
        "trip_theme": [
            "romantic", "family-vacation", "eco-tourism", "party", 
            "roadtrip", "remote-work", "business-work", "health and wellness", 
            "spiritual", "lbgtq+", "adventure", "general-tourism-no-theme"
        ],
        "traveller_type": [
            "solo", "couple", "family-no kids", "family-with kids", "friends"
        ],
        "budget": [
            "on a tight budget", "comfortable spending", 
            "happy to spend for a luxurious vacation"
        ],
        "food": [
            "any", "Middle-eastern", "indian", "asian", "european", 
            "mexican", "vegetarian", "south american", "vegan", 
            "seafood", "fast food", "cafe", "dessert", "healthy", 
            "bar/pub", "barbeque", "pizza"
        ],
        "trip_direction": [
            "return", "oneway"
        ],
        "optimizeType": [
            "manual", "auto"
        ],
        "time_schedule_duration_unit": [
            "week", "month", "days"
        ],
        "time_schedule_onward_trip_date_year": [
            "current_year", "next_year"
        ],
        "time_schedule_return_trip_date_year": [
            "current_year", "next_year"
        ]
    }
    if field_name in options_list:
        return options_list[field_name]
    else:
        return []


if __name__ == '__main__':
    app.run(debug=True)
