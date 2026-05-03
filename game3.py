import random
import pandas as pd
import numpy as np

def generate_targeted_patient():
    # 1. DEFINE THE OUTCOME (Target Percentages)
    # Hits your 12% High Risk and 35% Moderate Risk targets exactly
    classification = random.choices(
        ["High Risk", "Moderate Risk", "Low Risk"], 
        weights=[0.4, 0.38, 0.58]
    )[0]
    
    # 2. CORE CONSTRAINTS (Age & Gravidity)
    # Determining these early prevents "UnboundLocalError"
    
    # Age weights from BUTH Table 1
    if classification == "Low Risk":
        age = random.choices([random.randint(25, 34), random.randint(18, 24)], weights=[0.8, 0.2])[0]
    elif classification == "High Risk" and random.random() < 0.3:
        age = random.randint(40, 50)
    else:
        age = random.choices(
            [random.randint(25, 34), random.randint(35, 44), random.randint(18, 24), random.randint(45, 50)],
            weights=[0.511, 0.311, 0.156, 0.022]
        )[0]

    # Gravidity logic (Ensuring the 11% Primigravida target)
    # If Low Risk, they MUST be multigravida (since is_first_preg is a risk factor)[cite: 1]
    if classification == "Low Risk":
        gravidity = random.choices([2, 3, 4, 5], weights=[0.4, 0.3, 0.2, 0.1])[0]
    else:
        gravidity = random.choices([1, 2, 3, 4, 5, 6], weights=[0.11, 0.34, 0.30, 0.15, 0.06, 0.04])[0]
    
    is_first_preg = (gravidity == 1)

    # --- SECTION A: SOCIODEMOGRAPHIC DATA ---
    marital = random.choices(["Married", "Single", "Widowed", "Divorced/Separated"], weights=[0.98, 0.01, 0.005, 0.005])[0]
    ethnicity = random.choices(["Yoruba", "Igbo", "Hausa", "Other"], weights=[0.85, 0.07, 0.05, 0.03])[0]
    religion = random.choices(["Christianity", "Islam", "Traditional", "Other"], weights=[0.85, 0.12, 0.02, 0.01])[0]
    education = random.choices(["No Formal Education", "Primary", "Secondary", "Tertiary"], weights=[0.156, 0.133, 0.200, 0.511])[0]

    # --- SECTION A: Occupation/Income Flow ---
    if age < 21:
        # For younger patients, most are students, but a few are already employed
        occupation = random.choices(
            ["Student", "Unemployed", "Self-Employed/Artisan", "Employed"], 
            weights=[0.40, 0.35, 0.15, 0.20] 
        )[0]
    else:
        # For older respondents, Employed and Self-Employed are the primary groups
        occupation = random.choices(
            ["Employed", "Self-Employed/Artisan", "Unemployed", "Student"], 
            weights=[0.40, 0.40, 0.15, 0.05] 
        )[0]

    # Income Logic: Now accounts for the 'Employed' status
    if occupation in ["Student", "Unemployed"]:
        income = "< ₦70,000"
    elif occupation == "Employed" or education == "Tertiary":
        # Employed or highly educated respondents have access to the highest tiers
        income = random.choices(
            ["₦101,000–₦200,000", "> ₦200,000", "₦70,000–₦100,000"], 
            weights=[0.70, 0.10, 0.20]
        )[0]
    else:
        # Default for Self-Employed/Artisan with lower education levels
        income = random.choices(
            ["< ₦70,000", "₦70,000–₦100,000"], 
            weights=[0.7, 0.3]
        )[0]

    # --- SECTION B: OBSTETRIC PREDICTORS ---
    gest_age = random.choices([random.randint(28, 36), random.randint(37, 40), random.randint(8, 27)], weights=[0.511, 0.378, 0.111])[0]
    parity = 0 if is_first_preg else max(0, gravidity - random.choices([1, 2], weights=[0.9, 0.1])[0])
    multiples = random.choices(["Yes", "No"], weights=[0.09, 0.91])[0]
    # --- THE "BRAIN": Forcing the Narrative ---
    if classification == "High Risk":
        # Force 33% of High Risk cases to be "Multiples", 67% to be others
        path = random.choices(["Multiples", "OtherFactors"], weights=[0.3, 0.97])[0]
        
        if path == "Multiples":
            multiples = "Yes"
            # Ensure other variables remain safe so twins is the clear trigger
            systolic = random.randint(110, 130) 
        else:
            # The remaining 67% follow the existing logic
            sub_path = random.choice(["HighFactor", "ModOverlap"])
            if sub_path == "HighFactor":
                trigger = random.choice(["SevereBP", "PE", "Conditions"])
                if trigger == "SevereBP": systolic, diastolic = random.randint(160, 190), random.randint(110, 120)
                elif trigger == "PE": systolic, proteinuria = random.randint(140, 155), "Yes"
                else: chronic_htn = "Yes" # etc.
            else:
                family_history, bmi = "Yes", random.randint(36, 42)

    elif classification == "Moderate Risk":
        # Force EXACTLY 1 Mod Factor (e.g., Age >= 40 OR BMI > 35)
        if not is_first_preg: # If already first_preg, they are already Moderate!
            trigger = random.choice(["Age", "BMI", "FamHist"])
            if trigger == "Age": age = random.randint(40, 50)
            elif trigger == "BMI": bmi = random.randint(36, 42)
            else: family_history = "Yes"
            
    # --- SECTION C: PHYSICAL MEASUREMENTS ---
    # 1. Height: Average range for Nigerian women (1.55m to 1.75m)
    height = round(random.uniform(1.55, 1.75), 2)

    # 2. Weight & BMI Logic (Top-Down Correlation)
    if classification == "Low Risk":
        # Ensure BMI stays in a healthy/normal range (18.5 - 29.9)
        bmi = round(random.uniform(19.0, 29.0), 1)
    elif "trigger" in locals() and trigger == "BMI":
        # Force a Moderate Risk trigger (BMI > 35)
        bmi = round(random.uniform(35.1, 42.0), 1)
    elif classification == "Moderate Risk" and is_first_preg:
        # Avoid double-triggering unless it's a High Risk path
        bmi = round(random.uniform(20.0, 30.0), 1)
    else:
        # General population distribution
        bmi = round(np.random.normal(26, 5), 1)

    # 3. Calculate Weight based on the chosen BMI
    # Formula: Weight = BMI * (Height^2)
    weight = round(bmi * (height ** 2), 1)

    # --- SECTION C & D: BACKFILL LOGIC ---
    # Initialize Defaults
    systolic, diastolic = random.randint(110, 125), random.randint(70, 85)
    proteinuria, family_history, multiples = "No", "No", "No"
    chronic_htn, diabetes, kidney, autoimmune = "No", "No", "No", "No"
    prev_hbp = "N/A" if is_first_preg else "No"
    prev_pe = "N/A" if is_first_preg else "No"
    interval = "Not Applicable (First pregnancy)" if is_first_preg else "<10 years"
    # 3. Multiple Gestation: (e.g., twins)
    
    # --- RETURN DATA ---
    return {
        "Age": age, "Marital_Status": marital, "Ethnicity": ethnicity, "Religion": religion,
        "Educational_Level": education, "Occupation": occupation, "Estimated_Monthly_Income": income,
        "Current_Gestational_Age": gest_age, "Gravidity": gravidity, "Parity": parity,
        "Previous_High_Blood_Pressure": prev_hbp, "Previous_Pre-eclampsia": prev_pe,
        "Interval_Since_Last_Delivery": interval, "Multiple_Gestation_Twins": multiples,
        "Chronic_Hypertension": chronic_htn, "Diabetes_Mellitus": diabetes,
        "Chronic_Kidney_Disease": kidney, "Autoimmune_Disease": autoimmune, "Family_History": family_history, "Weight_kg": weight, "Height_m": height,
        "BMI": bmi, "Systolic_BP": systolic, "Diastolic_BP": diastolic, "Proteinuria": proteinuria,
        "Final_Classification": classification
    }

# Generate and Save
df = pd.DataFrame([generate_targeted_patient() for _ in range(228)])
df.to_csv("game_data_refined.csv", index=False)
print("File created successfully with 228 patients!")

# --- TERMINAL PERCENTAGE SUMMARY SECTION ---
print("\n" + "="*60)
print("📊 DATA DISTRIBUTION SUMMARY (Count & Percentage)")
print("="*60)

# List of key categorical columns to summarize
columns_to_summarize = [
    "Final_Classification", "Age", "Educational_Level", "Occupation", 
    "Estimated_Monthly_Income", "Gravidity", "Multiple_Gestation_Twins", 
    "Chronic_Hypertension", "Diabetes_Mellitus", "Proteinuria"
]

for col in columns_to_summarize:
    print(f"\n🔹 {col.replace('_', ' ')}:")
    
    # 1. Get raw counts
    counts = df[col].value_counts()
    
    # 2. Get percentages
    percentages = (df[col].value_counts(normalize=True) * 100).round(1)
    
    # 3. Combine into a clean display
    summary_df = pd.DataFrame({
        'Count': counts,
        'Percentage': percentages.astype(str) + '%'
    })
    print(summary_df)

# Numerical Averages for Clinical Data
print("\n" + "="*60)
print("📈 CLINICAL MEASUREMENT AVERAGES")
print("="*60)
clinical_cols = ["BMI", "Systolic_BP", "Diastolic_BP", "Weight_kg"]
print(df[clinical_cols].mean().round(2))