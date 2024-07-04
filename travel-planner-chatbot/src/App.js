import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

const initialJson = {
    "optimizeType": {},
    "firstDestination": {},
    "trip_theme": {},
    "destination": [],
    "traveller_type": {},
    "Origin_city": {},
    "budget": {},
    "food": {},
    "trip_direction": {},
    "time_schedule": {
        "onward_trip": {
            "time": {
                "hour": {},
                "minute": {}
            },
            "date": {
                "day_of_month": {},
                "month": {},
                "year": {}
            }
        },
        "return_trip": {
            "time": {
                "hour": {},
                "minute": {}
            },
            "date": {
                "day_of_month": {},
                "month": {},
                "year": {}
            }
        },
        "duration": {
            "value": {},
            "unit": {}
        }
    }
};

const App = () => {
    const [chatHistory, setChatHistory] = useState(["Bot: Hello! I am here to help you plan your vacation. Let's get started! Where are you planning to visit this time for vacation?"]);
    const [jsonData, setJsonData] = useState(initialJson);
    const [userInput, setUserInput] = useState('');
    const [options, setOptions] = useState([]);

    useEffect(() => {
        scrollToBottom();
    }, [chatHistory]);

    const scrollToBottom = () => {
        const chatContainer = document.getElementById('chat-container');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    };

    const handleUserInput = async (e) => {
        e.preventDefault();
        if (userInput.trim() === "") return;

        const newChatHistory = [...chatHistory, `User: ${userInput}`];
        setChatHistory(newChatHistory);
        setUserInput('');

        const response = await callOpenAIApi(newChatHistory);

        setChatHistory([...newChatHistory, `Bot: ${response?.next_reply}`]);
        setJsonData(response?.current_json);
        setOptions(response?.options);
    };

    const handleOptionClick = async (option) => {
        const newChatHistory = [...chatHistory, `User: ${option}`];
        setOptions([])
        setChatHistory(newChatHistory);

        const response = await callOpenAIApi(newChatHistory);

        setChatHistory([...newChatHistory, `Bot: ${response?.next_reply}`]);
        setJsonData(response?.current_json);
        setOptions(response?.options);
    };

    const callOpenAIApi = async (chatHistory) => {
        try {
            const response = await axios.post('http://127.0.0.1:5000/api/chat', {
                chat_history: chatHistory,
                jsonData: jsonData,
                options: options
            });

            return {
                current_json: response.data.current_json,
                next_reply: response.data.next_reply,
                options: response.data.options
            };
        } catch (error) {
            console.error("Error calling OpenAI API:", error);
            return {
                inferences: [],
                next_reply: "I'm sorry, I couldn't process your request. Please try again."
            };
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 p-8">
            <h1 className="text-3xl font-bold mb-6">Travel Planner Chatbot</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                    <h2 className="text-2xl font-semibold mb-4">Chatbot</h2>
                    <div id="chat-container" className="bg-white p-4 rounded shadow-md h-96 overflow-y-auto">
                        {chatHistory.map((chat, index) => (
                            <p key={index} className={chat.startsWith('Bot:') ? "text-blue-600" : "text-green-600"}>
                                {chat}
                            </p>
                        ))}
                        {options.length > 0 && (
                            <div className="flex flex-wrap mt-2">
                                {options.map((option, index) => (
                                    <button
                                        key={index}
                                        className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2 px-4 m-1 rounded cursor-pointer"
                                        onClick={() => handleOptionClick(option)}
                                    >
                                        {option}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                    <form onSubmit={handleUserInput} className="mt-4">
                        <input
                            type="text"
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            className="border border-gray-300 p-2 rounded w-full"
                            placeholder="Type your message..."
                        />
                        <button type="submit" className="mt-2 bg-blue-500 text-white px-4 py-2 rounded">
                            Send
                        </button>
                    </form>
                </div>
                <div>
                    <h2 className="text-2xl font-semibold mb-4">Current JSON Data</h2>
                    <pre className="bg-white p-4 rounded shadow-md h-96 overflow-y-auto">{JSON.stringify(jsonData, null, 2)}</pre>
                </div>
            </div>
        </div>
    );
};

export default App;
