import re
import os
import requests
import time
from pydantic import BaseModel
from bondai.tools import Tool

TOOL_NAME = 'phone_call_tool'
TOOL_DESCRIPTION = (
    "This tool interfaces allows you to make phone calls. The response you get back from this tool will be the call transcript.\n"
    "\nParameters:\n"
    "- phone_number (Required): The phone number of the person or company to call. For international numbers, "
    "include the country code without additional formatting (e.g., '+447700900077'). U.S. numbers may include "
    "formatting, but removing extra characters is recommended.\n"
    "- task (Required): This should be a highly detailed description of the task that should be performed on this call. Also, provide context about the interaction and give detailed instructions.\n"
    "- request_data (Optional, default={}): A dictionary that provides information for the AI during the call. Useful for giving the AI specific facts like the caller’s name, etc.\n"
)


BLAND_AI_API_KEY = os.environ.get('BLAND_AI_API_KEY')
BLAND_AI_VOICE_ID = int(os.environ.get('BLAND_AI_VOICE_ID', '0'))
BLAND_AI_CALL_TIMEOUT = int(os.environ.get('BLAND_AI_VOICE_ID', '300'))
API_ENDPOINT = 'https://api.bland.ai/'

# Interval for checking call status (in seconds)
CHECK_INTERVAL = 2


class CallParameters(BaseModel):
    phone_number: str
    task: str
    request_data: dict = {}
    thought: str




def validate_phone_number(phone):
    # International numbers (starting with '+')
    international_pattern = r'^\+\d{1,15}$'  # Starts with +, followed by 1 to 15 digits.

    # U.S. numbers (may include formatting characters)
    us_pattern = r'^(?:\+1)?[ -]?(\d{3})[ -]?(\d{3})[ -]?(\d{4})$'  # This considers formats like +1 123-456-7890, 123 456 7890, 123-456-7890.

    if re.match(international_pattern, phone):
        return True
    elif re.match(us_pattern, phone):
        return True
    else:
        error_msg = ("Invalid phone number format. "
                     "For international numbers, include the country code and exclude additional formatting. E.g. '+447700900077'. "
                     "For U.S. numbers, you may include formatting, but it's recommended to strip all additional characters.")
        raise ValueError(error_msg)


class BlandAITool(Tool):
    def __init__(self, bland_ai_api_key=BLAND_AI_API_KEY):
        super(BlandAITool, self).__init__(TOOL_NAME, TOOL_DESCRIPTION, CallParameters)
        self.bland_ai_api_key=bland_ai_api_key

    def run(self, arguments):
        if arguments.get('phone_number') is None:
            raise Exception("phone_number is required.")
        if arguments.get('task') is None:
            raise Exception("task is required.")

        validate_phone_number(arguments['phone_number'])

        # Start the call
        arguments['reduce_latency'] = False
        call_id = self.start_call(arguments)
        if not call_id:
            raise Exception("Failed to start the call.")
        
        # Monitor the call until completion
        start_time = time.time()
        while True:
            # Check for timeout
            elapsed_time = time.time() - start_time
            if elapsed_time > BLAND_AI_CALL_TIMEOUT:
                self.end_call(call_id)
                raise TimeoutError(f"Call exceeded the maximum allowed time of {BLAND_AI_CALL_TIMEOUT} seconds.")
            

            completed, transcripts = self.check_call_status(call_id)
            if completed:
                return f"Call to {arguments['phone_number']} has completed.\n\nTranscripts:\n{transcripts}"
            time.sleep(CHECK_INTERVAL)

    def start_call(self, arguments):
        headers = {'authorization': self.bland_ai_api_key}
        response = requests.post(API_ENDPOINT + 'call', json=arguments, headers=headers)
        if response.status_code == 200:
            resp_data = response.json()
            if resp_data["status"] == "success":
                return resp_data['call_id']
        return None

    def check_call_status(self, call_id):
        headers = {'authorization': self.bland_ai_api_key}
        data = {'call_id': call_id}
        response = requests.post(API_ENDPOINT + 'logs', json=data, headers=headers)
        
        if response.status_code == 200:
            resp_data = response.json()
            if resp_data['completed']:
                transcripts = "\n".join([f"{item['user']}: {item['text']}" for item in resp_data['transcripts']])
                return True, transcripts
        
        return False, None
    
    def end_call(self, call_id):
        headers = {'authorization': self.bland_ai_api_key}
        data = {'call_id': call_id}
        requests.post(API_ENDPOINT + 'end', json=data, headers=headers)

