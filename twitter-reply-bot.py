import tweepy
from airtable import Airtable
from datetime import datetime, timedelta
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import schedule
import time
import os
import pandas as pd  # For reading the Excel file

# Helpful when testing locally
from dotenv import load_dotenv
load_dotenv()

# Load your API keys from environment variables or defaults
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "YourKey")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "YourKey")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "YourKey")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv(
    "TWITTER_ACCESS_TOKEN_SECRET", "YourKey")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "YourKey")

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "YourKey")
AIRTABLE_BASE_KEY = os.getenv("AIRTABLE_BASE_KEY", "YourKey")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "YourKey")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YourKey")

# TwitterBot class to manage bot logic


class TwitterBot:
    def __init__(self):
        self.twitter_api = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN,
                                         consumer_key=TWITTER_API_KEY,
                                         consumer_secret=TWITTER_API_SECRET,
                                         access_token=TWITTER_ACCESS_TOKEN,
                                         access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
                                         wait_on_rate_limit=True)

        self.airtable = Airtable(
            AIRTABLE_BASE_KEY, AIRTABLE_TABLE_NAME, AIRTABLE_API_KEY)
        self.twitter_me_id = self.get_me_id()
        self.tweet_response_limit = 35  # Maximum tweets to respond to in a single run

        # Load the GPT model
        self.llm = ChatOpenAI(
            temperature=0.5, openai_api_key=OPENAI_API_KEY, model_name='gpt-4')

        # Load allowed usernames from an Excel file
        self.allowed_users = self.load_allowed_users("username.xlsx")

        # Stats tracking
        self.mentions_found = 0
        self.mentions_replied = 0
        self.mentions_replied_errors = 0

    def load_allowed_users(self, filepath):
        """Load allowed usernames from an Excel file."""
        df = pd.read_excel(
            filepath)  # Ensure the file exists and the 'username' column is present
        # Convert usernames to lowercase for consistent matching
        return set(df['username'].str.lower())

    def is_user_allowed(self, username):
        """Check if a username is in the allowed list."""
        return username.lower() in self.allowed_users

    def generate_response(self, mentioned_conversation_tweet_text):
        """Generate a professional response using GPT."""
        system_template = """
            You are a professional and articulate advisor with a deep understanding of technology trends. 
            Your goal is to provide concise, thoughtful, and insightful responses to the user's statements.
            
            % RESPONSE TONE:
            - Use a formal, informative, and polite tone.
            - Be precise, clear, and respectful in your communication.
            - Provide examples when necessary, but maintain clarity.
            
            % RESPONSE FORMAT:
            - Keep your response under 200 characters.
            - Limit your reply to one or two sentences.
            - No emojis.
        """
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            system_template)
        human_template = "{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(
            human_template)
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt])

        final_prompt = chat_prompt.format_prompt(
            text=mentioned_conversation_tweet_text).to_messages()
        response = self.llm(final_prompt).content

        return response

    def respond_to_mention(self, mention, mentioned_conversation_tweet):
        """Respond to a single mention."""
        response_text = self.generate_response(
            mentioned_conversation_tweet.text)

        try:
            response_tweet = self.twitter_api.create_tweet(
                text=response_text,
                in_reply_to_tweet_id=mention.id
            )
            self.mentions_replied += 1
        except Exception as e:
            print(f"Error responding to tweet: {e}")
            self.mentions_replied_errors += 1
            return

        # Log the response in Airtable
        self.airtable.insert({
            'mentioned_conversation_tweet_id': str(mentioned_conversation_tweet.id),
            'mentioned_conversation_tweet_text': mentioned_conversation_tweet.text,
            'tweet_response_id': response_tweet.data['id'],
            'tweet_response_text': response_text,
            'tweet_response_created_at': datetime.utcnow().isoformat(),
            'mentioned_at': mention.created_at.isoformat()
        })

    def get_me_id(self):
        """Get the bot's own user ID."""
        return self.twitter_api.get_me()[0].id

    def get_mention_conversation_tweet(self, mention):
        """Get the parent tweet of a mention."""
        if mention.conversation_id is not None:
            return self.twitter_api.get_tweet(mention.conversation_id).data
        return None

    def get_mentions(self):
        """Fetch recent mentions."""
        now = datetime.utcnow()
        start_time = now - timedelta(minutes=20)
        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        return self.twitter_api.get_users_mentions(
            id=self.twitter_me_id,
            start_time=start_time_str,
            expansions=['referenced_tweets.id'],
            tweet_fields=['created_at', 'conversation_id']
        ).data

    def check_already_responded(self, mentioned_conversation_tweet_id):
        """Check if a conversation ID is already logged in Airtable."""
        records = self.airtable.get_all(view='Grid view')
        for record in records:
            if record['fields'].get('mentioned_conversation_tweet_id') == str(mentioned_conversation_tweet_id):
                return True
        return False

    def respond_to_mentions(self):
        """Respond to mentions that are from allowed users."""
        mentions = self.get_mentions()
        if not mentions:
            print("No mentions found")
            return

        self.mentions_found = len(mentions)

        for mention in mentions[:self.tweet_response_limit]:
            user_username = mention.author.username
            if not self.is_user_allowed(user_username):
                print(f"Skipping user {user_username} (not in allowed list)")
                continue

            mentioned_conversation_tweet = self.get_mention_conversation_tweet(
                mention)
            if (mentioned_conversation_tweet.id != mention.id
                    and not self.check_already_responded(mentioned_conversation_tweet.id)):
                self.respond_to_mention(mention, mentioned_conversation_tweet)

    def execute_replies(self):
        """Main execution logic with logging."""
        print(f"Starting Job: {datetime.utcnow().isoformat()}")
        self.respond_to_mentions()
        print(f"Finished Job: {datetime.utcnow().isoformat()}, Found: {self.mentions_found}, "
              f"Replied: {self.mentions_replied}, Errors: {self.mentions_replied_errors}")


# Scheduled job logic
def job():
    print(f"Job executed at {datetime.utcnow().isoformat()}")
    bot = TwitterBot()
    bot.execute_replies()


if __name__ == "__main__":
    schedule.every(6).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
