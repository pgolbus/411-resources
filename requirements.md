# **Project Requirements for HW1**

## **Project Description**
This project will create Spotify playlists appropriate for the weather in a specified city. 
It will use the OpenWeatherMap API to get the current weather. A predefined dictionary 
will map weather conditions to Spotify genres. SQLite will store previous searches, 
city data, weather, and resulting playlists.

## **Goal**
Create an easy-to-use web interface that allows users to generate a Spotify playlist based on the local weather.

## **Non-Goal**
Dynamically predicting user music preferences using machine learning.

## **Non-Functional Requirements**
### **1. Security**
- **Functional Requirements:**
  - Implement OAuth authentication for secure user login.
  - Store API keys securely using environment variables.

### **2. Repeatability**
- **Functional Requirements:**
  - Store previous searches and results locally.
  - Ensure the same weather conditions generate the same playlist.

---

## **Agile User Stories**
### **Theme**: Delight the user by showing them a Spotify playlist appropriate to the local weather  
### **Epic**: Website Beta  

### **User Story 1**: As a new user, I want to feel comfortable using my Spotify account on Yet Another Website.
- **Task**: Use APIs securely  
  - **Ticket 1**: Safely store environment variables  
    - Ensure API keys are not exposed on the web.  
    - Research and implement best security practices.  
  - **Ticket 2**: Implement OAuth  
    - Implement OAuth login for Spotify.  

### **User Story 2**: As a repeat user, I want to be able to listen to my previous playlists.
- **Task**: Make previous playlists repeatable  
  - **Ticket 1**: Design and create a database for storing previous playlists.  
    - Use SQLite for storing past user searches and playlists.  
  - **Ticket 2**: Implement a Database Access Object (DAO)  
    - Abstract database operations to allow easy migration in the future.  

For now, we will use SQLite, but in the future, we might switch to another database solution. Abstracting database logic will allow seamless upgrades.

