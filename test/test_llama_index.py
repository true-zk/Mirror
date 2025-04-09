from functools import partial
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.agent.workflow import FunctionAgent, ReActAgent
from llama_index.core.tools import FunctionTool, ToolMetadata
from pydantic import BaseModel


class CCCCCAAAAA:
    def __init__(self, v=100):
        self.v = v

    def lalalal(self, a: float, b: float) -> float:
        """Multiply two numbers and returns the product"""
        return a * b + self.v
    
    def tool(self):
        class MultiplySchema(BaseModel):
            a: float
            b: float

        return FunctionTool.from_defaults(
            self.lalalal,
            name="multiply",
            description="Multiply two numbers and returns the product",
            fn_schema=MultiplySchema
            )
    

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

# from pydantic import BaseModel

# class MultiplySchema(BaseModel):
#     a: float
#     b: float

# # create function tool
# metadata = ToolMetadata(
#     name="multiply",
#     description="Multiply two numbers and returns the product",
#     fn_schema=MultiplySchema
# )
mul = CCCCCAAAAA()
# multiply = partial(mul.lalalal)


# multiply_tool = FunctionTool(
#     fn=multiply,
#     metadata=metadata
# )
multiply_tool = mul.tool()
add_tool = FunctionTool.from_defaults(fn=add)


workflow = FunctionAgent(
    tools=[multiply_tool, add_tool],
    llm=openai_llm,
    system_prompt="You are an agent that can perform basic mathematical operations using tools."
)


async def main():
    response = await workflow.run(user_msg="What is 20+(2*4)? Do you use multiply tool? Why? Use the multiply tool to calculate 2*4 and check if the answer is right.")
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())