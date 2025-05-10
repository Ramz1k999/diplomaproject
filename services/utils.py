def calculate_bmi_info(input_str):
    try:
        weight_str, height_str = input_str.split(',')
        weight = float(weight_str)
        height = float(height_str) / 100
        bmi = round(weight / (height ** 2), 1)

        if bmi < 18.5:
            category, advice, cal = "Underweight", "Try increasing calorie intake.", 2500
        elif bmi < 25:
            category, advice, cal = "Normal", "Great shape!", 2200
        elif bmi < 30:
            category, advice, cal = "Overweight", "Consider exercise & diet.", 1800
        else:
            category, advice, cal = "Obese", "Consult a specialist.", 1600

        return f"📊 BMI: *{bmi}* – {category}\n💡 {advice}\n🔥 Recommended daily calories: *{cal} kcal*"
    except:
        return "⚠️ Please enter weight and height like `70, 175`"

def calculate_water_intake(weight_str):
    try:
        weight = float(weight_str)
        liters = round((weight * 35) / 1000, 2)
        return f"💧 You should drink about *{liters} liters* of water per day."
    except:
        return "⚠️ Enter your weight as a number, e.g. `70`"
