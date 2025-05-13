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
            f"4. 💼 Occupation Note (impact o health if any)"
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
    Generates a beautifully formatted healthy recipe suggestion based on the given ingredients.
    """
    # Create a more structured prompt for consistent results
    prompt = f"""Create a healthy recipe using some or all of these ingredients: {', '.join(ingredients)}.

    Format your response exactly like this example, with all these sections:

    ## 🍲 [RECIPE NAME]

    ⏱️ **Prep Time:** [time] minutes | 🔥 **Cook Time:** [time] minutes | 🍽️ **Servings:** [number]

    ### 📋 Ingredients:
    • [ingredient 1 with measurement]
    • [ingredient 2 with measurement]
    • [etc...]

    ### 📝 Instructions:
    1. [step 1]
    2. [step 2]
    3. [etc...]

    ### 💪 Health Benefits:
    • [first health benefit]
    • [second health benefit]
    • [third health benefit]

    ### 📊 Nutrition (per serving):
    Calories: ~[number] | Protein: [number]g | Carbs: [number]g | Fat: [number]g

    Make the recipe quick and easy (under 30 minutes total), healthy, and use as many of the provided ingredients as possible. Be creative but practical.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini recipe error:", e)
        return "⚠️ Couldn't generate a recipe right now. Try again later."


def get_food_info(food: str) -> str:
    """
    Generates detailed, structured information about a given food item.
    """
    prompt = f"""Provide detailed nutritional information about {food}.
    Format your response with these exact sections:

    1. 🔍 OVERVIEW: Brief description of the food (2-3 sentences)
    2. 📊 NUTRITION: Key nutritional values per 100g (calories, protein, carbs, fat)
    3. 💪 HEALTH BENEFITS: 3 main health benefits (use bullet points)
    4. 👩‍⚕️ HEALTH CONSIDERATIONS: Any allergens, concerns, or moderation advice
    5. 🍽️ SERVING SUGGESTIONS: 2-3 healthy ways to include this in meals

    Keep each section brief but informative. Use emojis for visual appeal.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini food info error:", e)
        return f"⚠️ Couldn't fetch information about {food} right now. Please try again later."


def get_random_health_tip() -> str:
    """
    Generates a random health tip using Gemini.
    """
    prompt = """Generate a single short, practical health tip that is:
    1. Evidence-based and actionable
    2. No more than 120 characters 
    3. Focused on nutrition, exercise, mental health, or wellness
    4. Include an appropriate emoji at the beginning

    Format it as a single sentence without prefix or introduction.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Gemini health tip error:", e)
        # Fallback tips in case the API call fails
        fallback_tips = [
            "💧 Drinking water before meals can help with portion control and hydration.",
            "🚶 Walking for just 30 minutes a day can boost your cardiovascular health.",
            "🥗 Incorporate colorful fruits and vegetables into meals for diverse nutrients."
        ]
        return random.choice(fallback_tips)