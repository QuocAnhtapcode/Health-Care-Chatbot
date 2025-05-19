# Healthcare Chatbot

A healthcare chatbot application built with Flask, LangChain, and OpenAI.

## Prerequisites

- Python 3.8 or higher
- MySQL Server
- OpenAI API Key
- Pinecone API Key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd healthcare-chatbot
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following content:
```
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

5. Set up the MySQL database:
```sql
CREATE DATABASE healthcare;
USE healthcare;

CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Running the Application

1. Start the Flask application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:8080
```

## Project Structure

```
healthcare-chatbot/
├── services/
│   ├── chat_service/
│   ├── appointment_service/
│   ├── vector_store_service/
│   └── database_service/
├── templates/
├── static/
├── src/
├── app.py
├── requirements.txt
└── setup.py
```

## Development

- Use `black` for code formatting
- Use `flake8` for linting
- Use `pytest` for testing

## License

MIT 