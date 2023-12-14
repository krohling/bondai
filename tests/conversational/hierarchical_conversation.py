from bondai.models.openai import get_total_cost, OpenAILLM, OpenAIModelNames
from bondai.tools.file import FileWriteTool
from bondai.agents import ConversationalAgent
from bondai.agents.group_chat import (
    GroupConversation,
    TeamConversationConfig,
    UserProxy,
)

llm = OpenAILLM(OpenAIModelNames.GPT4_0613)

user_proxy = UserProxy()

agent_a1 = ConversationalAgent(
    name="A1",
    instructions="You are a team leader A1, your team consists of A2, A3. You can talk to your team members as well as the other team leader B1, whose team member is B2. Your team members have the values for x and y.",
    # llm=llm
)
agent_a2 = ConversationalAgent(
    name="A2",
    instructions="You are team member A2, you know the secret value of x but not y, x = 9. Tell others x to cooperate.",
    # llm=llm
)
agent_a3 = ConversationalAgent(
    name="A3",
    instructions="You are team member A3, You know the secret value of y but not x, y = 5. Tell others y to cooperate.",
    # llm=llm
)
agent_b1 = ConversationalAgent(
    name="B1",
    instructions="You are a team leader B1, your team consists of B2. You can talk to your team members as wel as the other team leader A1, whose team members are A2, A3.",
    # llm=llm
)
agent_b2 = ConversationalAgent(
    name="B2",
    instructions="You are team member B2. Your task is to find out the value of x and y from the other agents and compute the product. Once you have the answer you must save the value to a file named 'answer.txt' and share the answer with the user",
    tools=[FileWriteTool()],
    # llm=llm
)

conversation = GroupConversation(
    conversation_config=TeamConversationConfig(
        [agent_a1, agent_b1],
        [agent_a1, agent_a2, agent_a3],
        [agent_b1, agent_b2],
        [user_proxy, agent_b2],
    )
)

conversation.send_message(
    agent_b2.name,
    "Find the product of x and then notify the user. The other agents know x and y.",
)
print(f"Total Cost: {get_total_cost()}")
