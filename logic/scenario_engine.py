from openai import OpenAI
import os
from .prompts import SCENARIOS

class ScenarioEngine:
    def __init__(self, scenario_name: str = "scheduling"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.scenario_name = scenario_name
        self.system_prompt = SCENARIOS.get(scenario_name, SCENARIOS["scheduling"])
        self.history = [
            {"role": "system", "content": self.system_prompt}
        ]
        self.turn_count = 0
        self.max_turns = 10 # Prevent infinite loops

    def generate_response(self, user_transcript: str):
        """
        Generates the next response from the patient bot.
        """
        self.history.append({"role": "user", "content": user_transcript})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=self.history,
                max_tokens=150,
                temperature=0.7
            )
            bot_text = response.choices[0].message.content
            self.history.append({"role": "assistant", "content": bot_text})
            self.turn_count += 1
            return bot_text
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm sorry, I didn't catch that. Could you say it again?"

    def get_first_message(self):
        """
        Generates the opening line for the call.
        """
        # We prompt the LLM to start the conversation
        initial_instruction = "You are starting the call. The other side has just picked up and said 'Hello'. Introduce yourself and state your purpose based on your scenario."
        self.history.append({"role": "user", "content": initial_instruction})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=self.history,
                max_tokens=100
            )
            bot_text = response.choices[0].message.content
            self.history.append({"role": "assistant", "content": bot_text})
            return bot_text
        except Exception as e:
            return "Hello, I'm calling to make an appointment."

    def is_conversation_over(self):
        """
        Determines if the conversation should end.
        """
        if self.turn_count >= self.max_turns:
            return True
        
        # Check if the bot's last message indicates the conversation is ending
        last_message = self.history[-1]["content"].lower()
        
        # List of phrases that indicate the conversation is ending
        end_phrases = [
            "bye",
            "goodbye", 
            "have a good day",
            "have a great day",
            "see you",
            "talk to you later",
            "take care"
        ]
        
        for phrase in end_phrases:
            if phrase in last_message:
                print(f"Conversation ending detected: '{phrase}' found in: {last_message}")
                return True
                
        return False
        
    def get_transcript(self):
        """
        Returns the full conversation transcript.
        """
        return self.history
