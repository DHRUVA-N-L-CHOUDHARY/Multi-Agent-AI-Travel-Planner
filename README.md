
# Multi-Agent-AI-Travel-Planner

An AI-powered travel planner that leverages Agentic AI and collaborative LLM-based agents to automate and optimize the entire trip planning process — from searching flights and booking hotels to generating personalized itineraries.

## ✨ Introduction

As part of my journey to explore and master **Agentic AI**, I developed this travel planner application that automates the traditionally tedious and manual trip planning process. Instead of navigating across multiple websites to compare options, this system intelligently finds flights, books hotels, and creates a day-by-day itinerary — all powered by autonomous AI agents.

By leveraging **Large Language Models (LLMs)** and real-time data sources, the application showcases how multi-agent collaboration can streamline travel decisions and deliver an efficient, personalized experience.

## 🤖 What is Agentic AI?

**Agentic AI** refers to autonomous AI systems capable of:

* ✅ **Autonomous Decision Making** – Proactively acts without constant human commands.
* 🔄 **Multi-Agent Collaboration** – Specialized agents work together on different tasks.
* ⚡ **Scalability & Efficiency** – Parallel execution of tasks for faster output.
* 🌍 **Enhanced User Experience** – Smarter, context-aware decision making.

Unlike traditional models, Agentic AI dynamically makes real-time decisions, collaborates with other agents, and optimizes workflows using contextual data.

## 🚀 Key Features

### 1. 🛫 Flight Search Automation

* Fetches real-time flight data from **Google Flights** using **SerpAPI**.
* Filters by price, layovers, airlines, and travel time.
* AI recommends the most optimal flights based on user preferences.

### 2. 🏨 Hotel Recommendations

* Retrieves hotel availability via **Google Hotels**.
* Filters based on location, amenities, budget, and ratings.
* AI suggests hotels with the best value and convenience.

### 3. 🧠 AI-Powered Analysis & Recommendations

* Uses **Google Gemini LLM** for deep analysis of travel options.
* **Crew AI** coordinates multiple agents to ensure efficient decision-making.
* AI provides justifications and reasoning behind recommendations.

### 4. 📅 Dynamic Itinerary Generation

* Generates structured, day-by-day travel itineraries.
* Recommends must-visit attractions, restaurants, and transportation options.

### 5. 🔌 API-First Architecture

* Clean and simple **REST API** for flights, hotels, and itinerary generation.
* Can be integrated with any frontend (e.g. **Streamlit UI**).
  ![image](https://github.com/user-attachments/assets/11b07ef9-6f55-4dc6-ac09-d84b5f464448)

## 🛠️ Implementation Guide

### ✅ Pre-Requisites

Make sure you have the following set up:

* Python 3.8+
* [SerpAPI](https://serpapi.com/) Key – For real-time travel data
* [Google Gemini](https://aistudio.google.com/app/prompts/new_chat) API Key – For LLM recommendations
* [CrewAI](https://crewai.io/) – To orchestrate agent-based workflows

## 📸 Demo

![image](https://github.com/user-attachments/assets/59e6e2b3-e27d-4bfa-b2cf-24f12f82b335)
![image](https://github.com/user-attachments/assets/e50d3c97-47a7-4d07-8a81-a4b85416353e)

## 🧩 Tech Stack

* Python
* Gemini LLM (Google)
* SerpAPI (Google Flights/Hotels)
* CrewAI
* FastAPI (API layer)
* Streamlit (Frontend)

