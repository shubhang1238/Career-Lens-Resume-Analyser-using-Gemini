from google import genai

# Use your NEW Gemini API key here
client = genai.Client(api_key="GEMINI_API_KEY")

try:
    response = client.models.generate_content(
        model="gemini-3.8-flash", contents="Hello Gemini! Are you working?"
    )

    print("Gemini Response:")
    print(response.text)

except Exception as e:
    print("Error communicating with Gemini:")
    print(e)
