"""
Before run this example, ensure you have set the environment variable OPENAI_API_KEY.
You can obtain an API key by signing up at https://platform.openai.com/signup.
"""
from typing import List, Dict
import asyncio
from src.models.gpt_classifier import GptClassifier
from database.topic_controller import MsgData


async def run(msg_classifier: GptClassifier, msg_list: List[MsgData]) -> List[Dict]:
    """Predicts the classes of the input messages and prints the results."""
    results = await msg_classifier.predict(msg_list)

    for result in results:
        print(f"Message: {result['message'].msg_text}")
        print(f"Message Class: {result['msg_class']}")
        print(f"Process Status: {result['process_status']}")
        print(f"Prompt Tokens: {result['prompt_tokens']}")
        print(f"Completion Tokens: {result['completion_tokens']}")
        print(f"Time Spent: {result['time_spent']} seconds")
        print()


if __name__ == '__main__':
    classifier = GptClassifier()

    messages = [
        MsgData(1, 'For the moment we are focusing on open sourcing the things that allow developers to quickly build something using our API. We have published the code for our Android, iOS, web and desktop apps (Win, macOS and Linux) as well as the Telegram Database Library.', ''),
        MsgData(2, 'I recently graduated university and at this point haven’t had to read fiction for a class in over 2 years but I still can’t bring myself to read any classic literature even if I already know I enjoy the story. My brain has made such an intense association between classical writing styles and excessive hw/quizzes/papers that I can’t just relax and enjoy the book. Wondering if anyone else has this issue and how to get over it.', '')
    ]

    asyncio.run(run(classifier, messages))
