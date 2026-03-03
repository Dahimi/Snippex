from langchain_cerebras import ChatCerebras

llm = ChatCerebras(
    model="gpt-oss-120b",
    # other params...
)

print(llm.invoke("Hello, how are you?"))