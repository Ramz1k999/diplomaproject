import google.generativeai as genai
from typing import List

# Configure Gemini with your API key
genai.configure(api_key="AIzaSyDeebLjMVlINL7mmGYb7kf-I5rR6cNEDGE")

# Initialize the Gemini Pro model
model = genai.GenerativeModel("models/gemini-1.5-flash")


def handle_bmi_with_gemini(height: int, weight: int, age: int, occupation: str) -> str:
    """
    Generates a BMI-related health plan using Gemini, based on user's height, weight, age, and occupation.
    """
    try:
        bmi = weight / ((height / 100) ** 2)
        prompt = (
            f"You're a friendly fitness coach. My height is {height} cm, weight is {weight} kg, age is {age}, and I work as a {occupation}. "
            f"My BMI is {bmi:.1f}. Please keep your response short (under 100 words) and include emojis. Respond in this format:\n"
            f"1. 🧠 BMI Insight (1 sentence)\n"
            f"2. 🍽️ Daily Calorie Plan (short)\n"
            f"3. 💡 Health Tip (fun and useful)\n"
            f"4. 💼 Occupation Note (impact on health if any)"
        )
        response = model.generate_content(prompt)
        return f"🤖 *Your BMI is:* {bmi:.1f}\n{response.text.strip()}"
    except Exception as e:
        print("Gemini BMI error:", e)
        return "⚠️ Sorry, I couldn't get advice right now. Please try again later."



def get_water_reminder(height: int, weight: int) -> str:
    """
    Generates a water intake recommendation based on height and weight.
    """
    # Estimate water intake using weight (average: 35 ml per kg of body weight)
    water_intake = weight * 35  # in milliliters
    water_intake_liters = water_intake / 1000  # convert to liters

    return f"💧 You should drink about {water_intake_liters:.1f} liters of water daily."


def get_healthy_recipe(ingredients: List[str]) -> str:
    """
    Generates a healthy recipe suggestion based on the given ingredients.
    """
    prompt = (
            "User has the following ingredients: " + ", ".join(ingredients) + ".\n"
                                                                              "Suggest a healthy, quick recipe (under 30 min). Include name, steps, and benefits."
    )

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini recipe error:", e)
        return "⚠️ Couldn't generate a recipe right now. Try again later."


def get_food_info(food: str) -> str:
    """
    Generates information about a given food item.
    """
    prompt = f"Provide detailed nutritional and health information for {food}. Include health benefits, nutrients, and recommended usage."

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini food info error:", e)
        return "⚠️ Couldn't fetch food information right now. Try again later."
