from google import genai

# Use your NEW Gemini API key here
client = genai.Client(api_key="AQ.Ab8RN6L8aCpKlaaYr7gbuCqI3mlOwMsVxHVhqqtwPO32uD0FBg")

try:
    response = client.models.generate_content(
        model="gemini-3.8-flash", contents="Hello Gemini! Are you working?"
    )

    print("Gemini Response:")
    print(response.text)

except Exception as e:
    print("Error communicating with Gemini:")
    print(e)
