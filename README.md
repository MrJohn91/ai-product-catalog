# AI Product Catalog

## Overview

This is a small e-commerce product catalog app built with Streamlit. It displays a static list of products and allows users to filter by category, price, and rating. The standout feature is an AI-powered natural language search that extracts user intents and filters using the OpenAI GPT-3.5-turbo API.

## How to Run

1. Clone this repository.
2. Create a `.env` file in the project root containing your OpenAI API key:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```
4. Run the app:

   ```
   streamlit run app.py
   ```
5. Use the sidebar filters or type natural language queries in the search bar (e.g., "show me sports products under €100").

## AI Feature

* **Smart Product Search (NLP):** The app uses OpenAI's GPT-3.5-turbo to parse user queries in natural language and extract structured filters (category, price range, minimum rating, keywords). These filters dynamically narrow the product list, enhancing user search experience.

## Tools and Libraries

* Streamlit (UI)
* OpenAI Python SDK (GPT-3.5-turbo)
* Python standard libraries (json, os, re)
* python-dotenv (environment variable management)

## Assumptions

* The product catalog is static and loaded from a local JSON file.
* Basic sidebar filters complement the AI search.
* The app is intended as a demo prototype for e-commerce AI enhancements.

## Bonus Blockchain Integration Idea

The AI search and filtering engine can be extended with blockchain by enabling token-gated pricing, where holding certain tokens unlocks special discounts. User preferences and search behavior can be stored on-chain to allow personalized, decentralized recommendation engines and loyalty rewards implemented via smart contracts.