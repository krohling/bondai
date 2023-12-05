
#!/usr/bin/env python3
import os
import argparse
from termcolor import cprint
from bondai.util import ModelLogger
# from bondai.api import BondAIAPIServer
from bondai.models import LLM
from bondai.agents import (
    ConversationalAgent, 
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
from bondai.memory import (
    MemoryManager, 
    PersistentCoreMemoryDataSource, 
    InMemoryCoreMemoryDataSource
)
from .personas import (
    adversarial_agent as adversarial_agent_profile,
    coordination_agent as coordination_agent_profile,
    task_processing_agent as task_processing_agent_profile,
    user_liaison as user_liaison_profile,
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

# --server with optional port
parser.add_argument('--server', 
                    nargs='?', 
                    const='2663', 
                    metavar='server_port',
                    help='Starts the BondAI web server. If no port is specified, defaults to 5000.')

# --enable-prompt-logging with optional log_dir
parser.add_argument('--enable-prompt-logging', 
                    nargs='?', 
                    const='logs', 
                    metavar='log_dir',
                    help='Turns on prompt logging which will write all prompt inputs into the specified directory. Defaults to "logs" if no directory provided.')

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
    user_liaison_agent = ConversationalAgent(
        llm=llm,
        name=user_liaison_profile.NAME,
        persona=user_liaison_profile.PERSONA,
        persona_summary=user_liaison_profile.PERSONA_SUMMARY,
        instructions=user_liaison_profile.INSTRUCTIONS,
        tools=user_liaison_profile.TOOLS,
        memory_manager=MemoryManager(
            # core_memory_datasource=PersistentCoreMemoryDataSource(
            #     file_path="./.memory/user_liason_core_memory.json",
            #     sections={
            #         "user": "User's Name is unknown.",
            #         "task": "Task details unknown",
            #     }
            # )
        )
    )
    coordination_agent = ConversationalAgent(
        llm=llm,
        name=coordination_agent_profile.NAME,
        persona=coordination_agent_profile.PERSONA,
        persona_summary=coordination_agent_profile.PERSONA_SUMMARY,
        tools=coordination_agent_profile.TOOLS,
        enable_exit_conversation=False,
        memory_manager=MemoryManager(
            core_memory_datasource=InMemoryCoreMemoryDataSource(
                sections={
                    "task": "Task details unknown",
                    "agents": "Agent details unknown"
                }
            )
        )
    )
    task_processing_agent = ConversationalAgent(
        llm=llm,
        name=task_processing_agent_profile.NAME,
        persona=task_processing_agent_profile.PERSONA,
        persona_summary=task_processing_agent_profile.PERSONA_SUMMARY,
        tools=task_processing_agent_profile.TOOLS,
        enable_exit_conversation=False,
        memory_manager=MemoryManager(
            core_memory_datasource=InMemoryCoreMemoryDataSource(
                sections={
                    "task": "Task details unknown",
                    "feedback": "No feedback received"
                }
            )
        )
    )
    adversarial_agent = ConversationalAgent(
        llm=llm,
        name=adversarial_agent_profile.NAME,
        persona=adversarial_agent_profile.PERSONA,
        persona_summary=adversarial_agent_profile.PERSONA_SUMMARY,
        tools=adversarial_agent_profile.TOOLS,
        enable_exit_conversation=False,
        memory_manager=MemoryManager(
            core_memory_datasource=InMemoryCoreMemoryDataSource(
                sections={
                    "task": "Task details unknown",
                    "agents": "Agent details unknown"
                }
            )
        )
    )

    return GroupConversation(
        conversation_config = TeamConversationConfig(
            [user_proxy, user_liaison_agent],
            [user_liaison_agent, coordination_agent, adversarial_agent], 
            [coordination_agent, adversarial_agent, task_processing_agent]
        )
    )


def run_cli():
    try:
        llm=OpenAILLM(OpenAIModelNames.GPT4_0613)
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
                user_proxy = UserProxy()
                group_conversation = build_group_conversation(
                    user_proxy=user_proxy,
                    llm=llm
                )
                cprint("******************ENTERING CHAT******************", 'white')
                cprint("You are entering a chat with Ava. You can exit any time by typing 'exit'.", "white")
                intro_message = "The user has just logged in. Please introduce yourself in a friendly manner."
                group_conversation.send_message(
                    recipient_name=user_liaison_profile.NAME,
                    message=intro_message,
                )
            except KeyboardInterrupt:
                cprint(f"\n\nStopping BondAI CLI...\n", 'red')
        
    except BudgetExceededException as e:
        cprint(f"\n\nThe budget for this task has been exceeded and will stop.\n", 'red')
