import google.generativeai as genai
from typing import List

# Configure Gemini with your API key
genai.configure(api_key="YOUR_GEMINI_API_KEY")

# Initialize the Gemini Pro model
model = genai.GenerativeModel("gemini-pro")


def handle_bmi_with_gemini(height: int, weight: int) -> str:
    """
    Generates BMI-based health advice using Gemini.
    """
    bmi = weight / ((height / 100) ** 2)  # BMI formula
    bmi_category = ""

    if bmi < 18.5:
        bmi_category = "underweight"
    elif 18.5 <= bmi < 24.9:
        bmi_category = "normal weight"
    elif 25 <= bmi < 29.9:
        bmi_category = "overweight"
    else:
        bmi_category = "obese"

    prompt = (
        f"My BMI is {bmi:.1f}, I'm {height} cm tall and weigh {weight} kg. "
        f"Please suggest a daily calorie plan to help me reach a healthy weight and provide one nutrition tip."
    )

    try:
        response = model.generate_content(prompt)
        return f"Your BMI is {bmi:.1f} ({bmi_category}).\n{response.text.strip()}"
    except Exception as e:
        print("Gemini BMI error:", e)
        return "⚠️ Sorry, I couldn't get BMI advice right now. Please try again later."


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
