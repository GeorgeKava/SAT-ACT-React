# SAT-ACT React Application

## Overview
The **SAT-ACT React Application** is a web-based tool designed to assist students in preparing for the SAT and ACT exams. It provides functionality for solving problems in Math, Chemistry, Physics, SAT-specific sections, and ACT-specific sections. Users can input problems as text or capture them using a live video feed. The application leverages a Flask backend integrated with AI models to process and solve problems. This is based on the MathApp created using Flask and this project now utilizes React.js for frontend part of this web app. It should be noted that the subjects for Math, Chemistry, Physics have been commented out but you can enable them by commenting out the comments in the App.jsx and NavBar.jsx.

---

## Features
### Frontend
- **React-Based UI**: Built with React for a dynamic and responsive user experience.
- **Live Video Feed**: Allows users to capture problems using their webcam.
- **Subject-Specific Pages**:
  - Math
  - Chemistry
  - Physics
  - SAT
  - ACT
- **Navigation Bar**: Easy navigation between different subject pages.
- **Dynamic Problem Submission**:
  - Submit problems as text.
  - Capture problems via the live video feed.

### Backend
- **Flask API**: A Python-based backend that handles problem-solving requests.
- **AI Integration**:
  - Processes text and image-based problems using AI models.
  - Provides detailed, step-by-step solutions.
- **Endpoints**:
  - `/api/math`
  - `/api/chemistry`
  - `/api/physics`
  - `/api/SAT`
  - `/api/ACT`
  - `/api/video_feed` (for live video streaming)

---

## Installation

### Prerequisites
- **Node.js**: For running the React frontend.
- **Python 3.x**: For running the Flask backend.
- **pip**: Python package manager.
- **Azure OpenAI API Key**: Required for AI processing.

### Steps
1. **Clone the Repository**:
    git clone <repository-url>
    cd SAT-ACT-React
2. **Install Frontend Dependencies**:
    cd frontend
    npm install
3. **Install Backend Dependencies**:
    cd ../backend
    pip install -r requirements.txt
4. **Set Up Environment Variables**:
    There is a sample .env file where you can fill out the fields

5. **Start the Backend**:
    python app.py

6. **Start the Frontend**:
    cd ../frontend
    npm start

7. **Open the application**:
    Open the application in your browser at http://localhost:3000.

**File Structure**

SAT-ACT-React/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── NavBar.js
│   │   │   ├── MathPage.js
│   │   │   ├── ChemistryPage.js
│   │   │   ├── PhysicsPage.js
│   │   │   ├── SATPage.js
│   │   │   ├── ACTPage.js
│   │   ├── App.js
│   │   ├── index.js
│   ├── public/
│   ├── package.json
├── backend/
│   ├── app.py
│   ├── ai.py
│   ├── requirements.txt
│   ├── .env

**Usage**

1. **Navigate to a Subject Page**:
    * Use the navigation bar to select a subject (Math, Chemistry, Physics, SAT, or ACT).

2. **Submit a Problem**:
    * Enter a problem as text and click "Submit."
    * Alternatively, click "Show Video Feed," capture the problem, and click "Capture Problem."

3. **View the Solution**:
    * The solution will be displayed below the input form.

**Technologies Used**

Frontend
* React
* React Router
* Axios
* CSS for styling
Backend
* Flask
* Flask-CORS
* OpenAI API (Azure)
* OpenCV (for live video feed and image processing)

**Future Enhancements**
* Add user authentication for personalized problem-solving history.
* Improve UI/UX with advanced styling and animations.
* Add support for more subjects and problem types.
* Integrate additional AI models for enhanced problem-solving capabilities.
* Add a system where users can answer questions and get feedback if the question is right or wrong.

**License**
This project is licensed under the MIT License.

**Contributors**
George Kavalaparambil: Full-stack developer and project owner.