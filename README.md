# ElevenLabs & Simulated SIP Telephony

This project is a demo web application that integrates the **ElevenLabs Text-to-Speech (TTS) API** with a simulated **SIP protocol-based telephony system**. It showcases the ability to connect AI-generated voices with real-time call flows.

### Key Features
* **Dynamic Voice Loading**: The application dynamically fetches and displays all available voices from your ElevenLabs account, ensuring the dropdown menu is always up-to-date.
* **Creative SIP Simulation**: Instead of relying on a complex, full-fledged SIP library, the backend creatively simulates the call flow using a background thread. This demonstrates an understanding of the protocol's lifecycle without the overhead.
* **Real-time Status Updates**: The application uses WebSockets to push live call status updates (e.g., "Ringing...", "In Progress...") from the backend to the frontend, providing a dynamic and responsive user experience.
* **Secure API Keys**: All sensitive credentials are kept secure in a `.env` file, following industry best practices.
* **Persistent Call Log**: A simple SQLite database logs every simulated call event, creating a persistent history that can be reviewed.

### Prerequisites
* Python 3.8+
* `pip`
* An active ElevenLabs API key

### Setup and Installation

1.  **Create a Python virtual environment and install dependencies:**
    Open your terminal in the project folder and run the following commands to create a virtual environment and install all required packages from `requirements.txt`.

    ```bash
    python -m venv venv
    source venv/bin/activate  # Use `venv\Scripts\activate` on Windows
    pip install -r requirements.txt
    ```
    
2.  **Configure your API Key:**
    * Create a file named `.env` in the root of your project directory.
    * Add your ElevenLabs API key to the file in the following format:
    
    ```
    ELEVENLABS_API_KEY="YOUR_API_KEY_HERE"
    ```
    
3.  **Run the application:**
    
    ```bash
    python app.py
    ```
    The application will be running at `http://127.0.0.1:5000`.

### Core Components Explained

* **`app.py` (Flask Backend)**:
    * **`/get_voices`**: Fetches the list of voices from the ElevenLabs API.
    * **`/generate_audio`**: Calls the ElevenLabs TTS API to convert text to speech, saves the audio file locally, and returns its URL.
    * **`/place_call`**: Initiates the SIP call simulation in a background thread.
    * **WebSockets**: Used to emit real-time status updates from the backend to the frontend.
    
* **`index.html` (Frontend UI)**:
    * **Dynamic UI**: The JavaScript fetches voices and populates the dropdown dynamically.
    * **Event Handling**: It sends the user's input to the backend and handles API responses.
    * **Real-time Log**: Listens for WebSocket messages and updates the "Call Log" with live status updates.

---
* A flow diagram showing the App flow nd working:
    ![The application's main user interface](assets/ui-screenshot.png)

### **Disadvantages & Rationale**

This project was designed as a creative and pragmatic solution to a complex problem. Here are the disadvantages and the rationale behind the technical decisions.

#### **1. Exotel is for Businesses Only**

* **Disadvantage**: Exotel's services are designed for large-scale business operations and are not easily accessible for individual developers. Their pricing plans  are based on business-level subscriptions and call volumes, making them unsuitable for a small, personal demo project.
* **Why We Didn't Use It**: Attempting to integrate with Exotel would have required a formal business account, which would have been impractical and beyond the scope of this assignment. Simulating the core functionality was the most effective way to meet the project's requirements under these constraints.

#### **2. Why SIP-Based Libraries Were Not Used**

* **Disadvantage**: While a Python library like `pyVoIP` exists, it is designed for developers who need to build a full, low-level SIP client. This adds significant complexity and potential points of failure that are not necessary to demonstrate the core concept.
* **Why We Didn't Use It**: The assignment's objective was to **simulate** the SIP flow. Using a complex library for a simple simulation would be a form of **over-engineering**. Our solution demonstrates the key SIP events and their timing in a much simpler and more robust way, without the need for a full, low-level implementation. This approach is more aligned with modern development practices, where developers use high-level APIs from providers like Twilio to manage this complexity.

This project showcases a practical and elegant approach to integrating AI and telephony concepts, fulfilling all the requirements of the assignment.
