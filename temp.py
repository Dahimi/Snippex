from langchain_cerebras import ChatCerebras
from dotenv import load_dotenv
load_dotenv()
llm = ChatCerebras(
    model="qwen-3-235b-a22b-instruct-2507",
    # other params...
)

print(llm.invoke("Hello, how are you?"))