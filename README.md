# TwitterBot

A Twitter bot that automatically responds to mentions with professional, GPT-generated replies. This bot filters mentions based on an allowed users list and logs interactions in Airtable. The bot runs periodically and responds to mentions with a formal and informative tone—clear, concise, and respectful.

## Features

- Responds to mentions on Twitter.
- Filters mentions by allowed users (based on an Excel file).
- Generates professional, polite responses using GPT-4.
- Logs interactions in Airtable.
- Prevents duplicate replies by checking Airtable for already responded mentions.
- Runs every 6 minutes to check for new mentions and respond accordingly.

## Prerequisites

Before running this bot, ensure you have the following:

- Python 3.7+
- Twitter Developer API credentials
- Airtable API key and base
- OpenAI API key
- `.env` file to store sensitive information (API keys, etc.)

### Required Libraries

- `tweepy`: For interacting with Twitter's API.
- `airtable-python-wrapper`: For Airtable API integration.
- `langchain`: For generating responses using OpenAI GPT.
- `schedule`: For scheduling the bot to check for mentions periodically.
- `pandas`: To load and filter the list of allowed users from an Excel file.
- `dotenv`: To load environment variables securely.

### Install Dependencies

To install the necessary libraries, run:

``` bash
pip install -r requirements.txt
```

### Setup
Create a .env file in the project root directory to store your API keys and credentials:
```ini
TWITTER_API_KEY=YourTwitterAPIKey
TWITTER_API_SECRET=YourTwitterAPISecret
TWITTER_ACCESS_TOKEN=YourTwitterAccessToken
TWITTER_ACCESS_TOKEN_SECRET=YourTwitterAccessTokenSecret
TWITTER_BEARER_TOKEN=YourTwitterBearerToken

AIRTABLE_API_KEY=YourAirtableAPIKey
AIRTABLE_BASE_KEY=YourAirtableBaseKey
AIRTABLE_TABLE_NAME=YourAirtableTableName

OPENAI_API_KEY=YourOpenAIAPIKey
```

Prepare an Excel file (username.xlsx) containing the list of allowed Twitter usernames you want the bot to interact with. The file should contain a column named username.

### Schedule the Bot:
The bot is set to run every 6 minutes using the schedule library. The logic for fetching mentions and replying is handled within the TwitterBot class.


### How It Works
1. Initialization:
The bot authenticates with Twitter using the credentials provided in the .env file.
It loads the list of allowed usernames from username.xlsx.
2. Check Mentions:
Every 6 minutes, the bot fetches recent mentions of its Twitter account (tweets that tag the bot).
It filters mentions to only respond to those from allowed users.
3. Generate Response:
For each valid mention, the bot generates a professional response using GPT-4 (through LangChain).
The response is generated in a formal, clear, and polite tone.
4. Reply to Mention:
The bot replies to the tweet with the generated response.
The interaction is logged in Airtable, which includes:
The original tweet's ID and text.
The response tweet's ID and text.
Timestamp details for when the tweet was created.
5. Prevent Duplicate Responses:
Before replying, the bot checks Airtable to ensure it hasn’t already responded to that mention.
6. Repeat:
This process repeats every 6 minutes, ensuring the bot stays active and responsive.
Running the Bot

After setting up the necessary files and credentials, you can run the bot with the following command:
```bash
python twitter_reply_bot.py
```
The bot will continuously run and execute every 6 minutes. You can stop it manually when needed (e.g., with CTRL+C).

Example Output
When the bot runs, you’ll see logs like the following:

```yaml
Job executed at 2025-01-09T12:00:00Z
Starting Job: 2025-01-09T12:00:00Z
Responding to mention from @user1: "What’s the best tech of 2025?"
Generated response: "As technology evolves, some older tools are still quite valuable. Stay informed for emerging trends."
Responding to tweet...
Finished Job: 2025-01-09T12:00:06Z, Found: 2, Replied: 2, Errors: 0
```

