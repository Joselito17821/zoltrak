import ollama

respuesta = ollama.chat(
    model='llama3.2:3b',
    messages=[
        {'role': 'user', 'content': 'Hola, preséntate en una frase'}
    ]
)

print(respuesta['message']['content'])
