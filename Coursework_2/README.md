# Assessment Planner

A Flask-based web application for managing assessments. Users can add, edit, view, and delete assessments, mark them as complete or incomplete, and sort them if needed.

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [Project Structure](#project-structure)
4. [Features](#features)
5. [Known Issues](#known-issues)
6. [License](#license)

## Installation

1. Clone the repository
2. Set up a virtual environment
3. Install the dependencies (requirements.txt)

## Usage

1. Create the database
2. Run the Flask application
3. Access the application on your web browser

## Project Structure

Coursework_1/
├── app/
│   ├── __init__.py
│   ├── db_create.py
│   ├── forms.py
│   ├── models.py
│   ├── views.py
│   ├── __pycache__/
│   ├── static/
│   │   ├── planner_icon.ico
│   │   ├── scripts.js
│   │   └── styles.css
│   └── templates/
│       ├── add_assessment.html
│       ├── base.html
│       ├── edit_assessment.html
│       └── home.html
├── migrations/
├── tmp/
├── app.db
├── config.py
├── README.md
├── requirements.txt
└── run.py

## Features

- Add, edit, delete assessments.
- Mark assessments as complete or incomplete.
- Filter (by search) and sort assessments by deadline.
- Responsive web interface built using Bootstrap.
- Professional-looking design based on my own css + js.
