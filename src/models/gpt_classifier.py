from typing import List
import asyncio
import time
import yaml
from loguru import logger
from openai import AsyncOpenAI, OpenAIError
from src.config import GPT_VERSION, OPENAI_API_KEY, OPENAI_OPTIONS


class GptClassifier:
    """A class for categorizing messages using the OpenAI GPT model.

    Attributes:
        client: An instance of AsyncOpenAI for interacting with the OpenAI API.
        timelimit: An integer representing the maximum time limit for API calls.
        msg_classes: A dictionary mapping message classes to their respective prompts.
        prompt_template: A string template for generating prompts.
    """
    def __init__(self):
        """Initialize the GptClassifier."""
        try:
            self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            self.timelimit: int = 5

            with open('prompts.yml', 'r', encoding='utf-8') as f:
                prompt_config = yaml.safe_load(f)

            self.msg_classes = prompt_config['msg_classes']
            self.prompt_template = prompt_config['msg_classification_prompt']
        except FileNotFoundError as e:
            print(f'Config file not found: {e}')
            raise
        except yaml.YAMLError as e:
            print(f'Error loading YAML file: {e}')
            raise
        except KeyError as e:
            print(f'Key not found in config file: {e}')
            raise
        except OpenAIError as e:
            logger.exception(f'Error during OpenAI client initialization: {e}')
            raise
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            raise

    async def predict(self, messages: List[str]) -> List[dict]:
        """Predict the class of input messages.

        Args:
            messages: A list of strings representing messages to classify.

        Returns:
            A list of dictionaries for every message of the following structure:
            {
                "message": str or None,     # Message for categorization
                "msg_class": str or None,   # Predicted message class or None if not classified
                "process_status": str,      # Process status, including any errors or warnings.
                "prompt_tokens": int,       # Number of tokens used in the prompt
                "completion_tokens": int,   # Number of tokens in the completion
                "time_spent": float         # Time spent processing the message in seconds
            }
        """
        if not messages:
            return [
                {
                    "message": None,
                    "msg_class": None,
                    "process_status": "Empty input.",
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "time_spent": 0
                }
            ]

        # create task for each message
        tasks = [self._predict_message(msg) for msg in messages]

        # run all tasks concurrently
        results = await asyncio.gather(*tasks)

        return results

    def _create_prompt(self, message: str) -> str:
        """Create a prompt for the given message.

        Args:
            message: A string representing the input message.

        Returns:
            A string representing the prompt.
        """
        prompt = self.prompt_template.format(
            msg_classes = self.msg_classes,
            msg_text = message
        )

        return prompt

    async def _predict_message(self, message: str) -> dict:
        """Predict the class of a single message.

        Args:
            message: A string representing the input message.

        Returns:
            A dictionary containing the message, predicted class, process status,
            prompt tokens, completion tokens, and time spent for the message.
        """
        # record the start time
        start_time = time.time()
        time_spent = None

        # initialize response variables
        pred_msg_class = None
        process_status = "ok"
        prompt_tokens = 0
        completion_tokens = 0

        # crop long message
        text = message[:1024]

        prompt = self._create_prompt(text)

        try:
            logger.debug('The request has been sent to the OpenAPI')

            # call the _api_call method with a timeout
            response = await asyncio.wait_for(
                self._api_call(prompt), timeout=self.timelimit
            )

            # process OpenAI response
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            response_text = response.choices[0].message.content
            pred_msg_class = str(response_text).strip().lower()
            time_spent = round(time.time() - start_time, 2)

            if pred_msg_class not in self.msg_classes:
                pred_msg_class = None
                process_status = f'Couldn\'t interpret the OpenAI response: {response_text}'
                logger.error(process_status)

            logger.debug('Succesfully received a response from OpenAI')

        except asyncio.TimeoutError:
            # if the request times out
            time_spent = round(time.time() - start_time, 2)
            process_status = f'The response timed out and was aborted after {self.timelimit} sec.'
            logger.error(process_status)
        except OpenAIError as e:
            time_spent = round(time.time() - start_time, 2)
            process_status = f'OpenAI API Error: {e}'
            logger.exception(process_status)
        except Exception as e:
            time_spent = round(time.time() - start_time, 2)
            process_status = f'An unexpected error occurred: {e}'
            logger.exception(process_status)

        return {
            'message': text,
            'msg_class': pred_msg_class,
            'process_status': process_status,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'time_spent': time_spent
        }

    async def _api_call(self, prompt: str):
        """Make a call to the OpenAI API.

        Args:
            prompt: A string representing the prompt to send to the API.

        Returns:
            The response from the OpenAI API.
        """
        logger.info("Send a request to the OpenAI API ...")

        response = await self.client.chat.completions.create(
            model=GPT_VERSION,
            messages=[{"role": "user", "content": prompt}],
            **OPENAI_OPTIONS
        )

        return response
