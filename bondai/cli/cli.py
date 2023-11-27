
#!/usr/bin/env python3
import os
import argparse
from termcolor import cprint
from bondai.util import ModelLogger
# from bondai.api import BondAIAPIServer
from bondai.models import LLM
from bondai.agents import (
    Agent, 
    ConversationMember, 
    BudgetExceededException
)
from bondai.agents.group_chat import (
    GroupConversation, 
    TeamConversationConfig, 
    UserProxy
)
from bondai.models.openai import (
    OpenAILLM, 
    OpenAIModelNames,
    OpenAIConnectionType,
    enable_logging,
    OPENAI_CONNECTION_TYPE,
)
from .personas import (
    user_liaison, 
    team_leader, 
    strategic_planner,
    ALL_PERSONAS
)

if OPENAI_CONNECTION_TYPE == OpenAIConnectionType.OPENAI and not os.environ.get('OPENAI_API_KEY'):
    cprint(f"The OPENAI_API_KEY environment variable has not been set. Please input your OpenAI API Key now or type 'exit'.", 'yellow')
    user_input = input()
    if user_input == 'exit':
        exit(1)
    else:
        import openai
        openai.api_key = user_input




cprint(f"Loading BondAI...", 'white')

parser = argparse.ArgumentParser(description="BondAI CLI tool options")

parser.add_argument('--server', 
                    nargs='?', 
                    const='2663', 
                    metavar='server_port',
                    help='Starts the BondAI web server. If no port is specified, defaults to 5000.')

parser.add_argument('--enable-dangerous', 
                    action='store_true', 
                    help='Allows potentially dangerous Tools to be loaded (i.e. ShellTool and PythonREPLTool)')

# --enable-prompt-logging with optional log_dir
parser.add_argument('--enable-prompt-logging', 
                    nargs='?', 
                    const='logs', 
                    metavar='log_dir',
                    help='Turns on prompt logging which will write all prompt inputs into the specified directory. Defaults to "logs" if no directory provided.')

# --load-tools with specified Python file
parser.add_argument('--load-tools', 
                    metavar='my_tools.py', 
                    help='Specify a Python file to load tools from. The file should have a function named get_tools() that returns a list of Tools.')

 # --quiet
parser.add_argument('--quiet', 
                    action='store_true', 
                    default=False,
                    help='If set, minimizes the output to the console.')

args = parser.parse_args()


if args.enable_prompt_logging:
    log_dir = args.enable_prompt_logging
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    enable_logging(ModelLogger(log_dir))
    cprint(f"Prompt logging is enabled. Logs will be written to: {log_dir}", "yellow")

def build_group_conversation(llm : LLM, user_proxy: ConversationMember) -> GroupConversation:
    user_liaison_agent = Agent(
        name=user_liaison.NAME,
        persona=user_liaison.PERSONA,
        persona_summary=user_liaison.PERSONA_SUMMARY,
        tools=user_liaison.TOOLS,
        llm=llm,
    )
    team_leader_agent = Agent(
        name=team_leader.NAME,
        persona=team_leader.PERSONA,
        persona_summary=team_leader.PERSONA_SUMMARY,
        tools=team_leader.TOOLS,
        llm=llm,
    )
    strategic_planner_agent = Agent(
        name=strategic_planner.NAME,
        persona=strategic_planner.PERSONA,
        persona_summary=strategic_planner.PERSONA_SUMMARY,
        tools=strategic_planner.TOOLS,
        llm=llm,
    )
    
    team_1 = [user_proxy, user_liaison_agent]
    team_2 = [user_liaison_agent, team_leader_agent, strategic_planner_agent]
    team_3 = [team_leader_agent]
    for persona in ALL_PERSONAS:
        if persona.NAME != user_liaison.NAME:
            print(f"Adding {persona.NAME} to team 3")
            print(persona.TOOLS)
            agent = Agent(
                name=persona.NAME,
                persona=persona.PERSONA,
                persona_summary=persona.PERSONA_SUMMARY,
                tools=persona.TOOLS,
                llm=llm,
            )
            team_3.append(agent)

    return GroupConversation(
        conversation_config = TeamConversationConfig(team_1, team_2, team_3)
    )


def run_cli():
    try:
        llm=OpenAILLM(OpenAIModelNames.GPT4_TURBO_1106)
        if args.server:
            port = int(args.server)
            # user_proxy = UserProxy()
            # group_conversation = build_group_conversation(
            #     user_proxy=user_proxy,
            #     llm=llm
            # )
            # server = BondAIAPIServer(
            #     group_conversation=group_conversation, 
            #     port=port
            # )

            # try:
            #     server.run()
            # except KeyboardInterrupt:
            #     cprint(f"\n\nStopping BondAI server...\n", 'red')
        else:
            try:
                message = "Please introduce yourself to the user."
                user_proxy = UserProxy()
                group_conversation = build_group_conversation(
                    user_proxy=user_proxy,
                    llm=llm
                )
                group_conversation.send_message(
                    recipient_name=user_liaison.NAME,
                    message=message,
                )
            except KeyboardInterrupt:
                cprint(f"\n\nStopping BondAI CLI...\n", 'red')
        
    except BudgetExceededException as e:
        cprint(f"\n\nThe budget for this task has been exceeded and will stop.\n", 'red')
