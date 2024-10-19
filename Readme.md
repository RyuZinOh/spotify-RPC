# Spot That

## Project Overview
Spot That is a simple web application that integrates with Spotify to display currently playing tracks. This project serves as a test site to mimic production-level functionality.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Notes](#notes)

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/RyuZinOh/spotify-RPC
   cd "repo name"
   ```

2. **Create a Virtual Environment (Optional)**
   If you want to create a virtual environment, run:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   Ensure you have the necessary packages by running:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the root directory and add the required environment variables according to the setup in `app.py`.

5. **Run the Application**
   Start the application using:
   ```bash
   python app.py
   ```

## Usage
Once the application is running, you can access it in your browser at `http://localhost:5000`. 

### Important Notes
- If you choose to use the global deployed version of this project, please note that your Spotify credentials may be stored on my cloud database. However, this may lead to unauthorized requests until I manually verify your access in my Spotify developer dashboard.
- Keep in mind that this is a non-production site with a limit of 25 users for testing purposes. 


### I want to add
1. a searching feature to search all the user and see their status
2. more refined version of bad request  as a error handler

u can fork this and make adjustment, and we can merge the project until its completed  

Thank you for your understanding!

