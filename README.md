# cheating-detection-system

# AI-Powered Cheating Detection System

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Future Enhancements](#future-enhancements)
- [Contributors](#contributors)

---

## Overview
The AI-Powered Cheating Detection System is designed to enhance academic integrity by leveraging computer vision techniques to identify cheating behaviors in examination halls. This project is part of the **'Transforming VIT into an AI-Powered Smart Campus'** hackathon track. The system utilizes **YOLO-based object detection** to detect unauthorized materials like **mobile phones, laptops, books, and chits (cheating papers)** in real-time.

---

## Features
 **Real-time Cheating Detection** - Detects electronic devices, books, and chits using AI-powered vision models.  
 **Custom YOLO Model Training** - Fine-tuned detection for chits and other unauthorized objects.  
 **Live Video Stream Analysis** - Processes live camera feeds for real-time monitoring.  
 **Automated Reporting System** - Flags suspicious activities and logs detected violations.  
 **Scalable & Efficient Backend** - Alternative to Firebase for cost-effective implementation.  

---

## Technology Stack
- **Machine Learning**: YOLO (You Only Look Once) for object detection  
- **Backend**: Flask/FastAPI (alternative to Firebase)  
- **Frontend**: React.js (for dashboard integration)  
- **Database**: PostgreSQL / MongoDB  
- **Cloud Storage**: TBD  

---

## Installation
### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/cheating-detection.git
cd cheating-detection
```

### 2. Set Up Virtual Environment
```bash
python -m venv my_project_env
source my_project_env/bin/activate  # For Linux/macOS
my_project_env\Scripts\activate  # For Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Detection System
```bash
python main.py
```
Contributors:
Nitheeshwar: Front-End API
Anmol Sheth: AI detection + backend
Afthab: Backend + Database 
Aditya: Testing videos

