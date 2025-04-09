# Description: Test OpenAI API
# chat: most models are supported
# create: local-qwen
# embedding: text-embedding-v1, Embedding-V1, bge-*, qwen-*, ali-stable-diffusion-*, wanx-v1
# images: cogview-3, wanx-v1
import requests
from time import time

from openai import OpenAI

api_key = "sk-iQn5lQPRtgZRKu56D787847152A34d8aB14dEa157e79FeBf"
url = "http://111.186.56.172:3000/v1"


def timer(func):
    def wrapper(*args, **kwargs):
        tik = time()
        res = func(*args, **kwargs)
        tok = time()
        print(f">>>>>>>>>>> Func {func.__name__}, Time taken: {tok - tik} s")
        return res
    return wrapper


client = OpenAI(
        base_url=url,
        api_key=api_key
    )


def get_models():
    models = client.models.list()
    for model in models:
        print(model.id)


def get_model_info(model="deepseek-chat"):
    model = client.models.retrieve(model)
    print(model)


def test_all_models(func):
    for model in client.models.list():
        print(f"Testing model: {model.id}")
        try:
            func(model.id)
        except Exception as e:
            print(f"Error: {e}")


@timer
def test_chat(model="deepseek-chat"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Who are u? Are u able to access the Internet?"}]
    )
    print(response.choices[0].message.content)
    with open("test_chat.txt", "w") as f:
        f.write("Prompt:\n Who are u? Are u able to access the Internet?\n")
        f.write("Response:\n ")
        f.write(response.choices[0].message.content)


@timer
def test_create(model="local-qwen"):
    """local-qwen can be used"""
    response = client.completions.create(
        model=model,
        prompt="Once upon a time",
        max_tokens=200,
        echo=True,
        temperature=0.5,
    )
    print(response.choices[0].text)
    with open("test_create.txt", "w") as f:
        f.write("Prompt:\n Once upon a time\n")
        f.write("Response:\n ")
        f.write(response.choices[0].text)


@timer
def test_embedding(model="text-embedding-v1"):
    """For text-embedding-v1, fixed dimension: 1536"""
    response = client.embeddings.create(
        model=model,
        input=["Hello world", "How are you?"],
    )
    print(len(response.data[0].embedding))
    with open("test_embedding.txt", "w") as f:
        f.write("Input:\n Hello world\n How are you?\n")
        f.write("Embedding:\n ")
        f.write(str(response.data))


@timer
def test_img_gen(model="cogview-3"):
    """wanx-v1 cogview-3 are supported for image generation"""
    response = client.images.generate(
        model=model,
        prompt="A fictional creature",
        n=1,
    )
    print(response.data[0].url)
    with open("test_img_gen.jpg", "wb") as f:
        f.write(requests.get(response.data[0].url).content)


get_models()
get_model_info()
test_chat("qwen-max-longcontext")
test_create()
test_embedding()
test_img_gen("wanx-v1")
