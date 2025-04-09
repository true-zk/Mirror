from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.agent.workflow import FunctionAgent

def multiply(a: float, b: float) -> float:
    """Multiply two numbers and returns the product"""
    return a * b

def add(a: float, b: float) -> float:
    """Add two numbers and returns the sum"""
    return a + b

# llm = DashScope(
#         model_name=DashScopeGenerationModels.QWEN_MAX,
#         api_key="sk-37bc2f5cc0f34745a49caed5f99e7432"
#     )

openai_llm = OpenAILike(
        model="qwen-max",
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        is_chat_model=True,
        is_function_calling_model=True,
        api_key="sk-37bc2f5cc0f34745a49caed5f99e7432"
    )

# resp = llm.complete("How to make cake?")
# print(resp)

workflow = FunctionAgent(
    tools=[multiply, add],
    llm=openai_llm,
    system_prompt="You are an agent that can perform basic mathematical operations using tools."
)

async def main():
    response = await workflow.run(user_msg="What is 20+(2*4)?")
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())