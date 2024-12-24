from groq import Groq

# Initialize the Groq client
client = Groq()


def invoke_groq(prompt, system_prompt="you are a helpful assistant.", is_json=False):
    """
    Invokes the ChatGroq model with a given prompt.
    """
    # Use the client to create a chat completion
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        model="llama3-70b-8192",  # Specify the desired model
        temperature=0,
        max_tokens=8192,
        top_p=1,
        stop=None,
        stream=False,
        response_format={"type": "json_object"} if is_json else None,
    )

    # Return the generated content
    return chat_completion.choices[0].message.content
