
import ollama

response = ollama.chat(
    model="qwen3:0.6b",
    messages=[
        {
            "role": "user",
            "content": "Explain ETL in exactly two sentences."
        }
    ]
)

print("\nQwen Response:")
print(response["message"]["content"])
