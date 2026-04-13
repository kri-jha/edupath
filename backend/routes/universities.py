from fastapi import APIRouter
from pydantic import BaseModel
import json
import os

router = APIRouter()

# Load universities data
data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "universities.json")
try:
    with open(data_file, "r") as f:
        universities_data = json.load(f)
except:
    universities_data = []

class ProfileMatch(BaseModel):
    gpa: float
    target_country: str
    target_course: str

@router.get("/universities")
def get_universities(country: str = None, max_cost: int = None):
    result = universities_data
    if country and country.lower() != "all":
        result = [u for u in result if u["country"].lower() == country.lower()]
    if max_cost:
        result = [u for u in result if u["annual_cost_inr"] <= max_cost]
    return result

@router.post("/universities/recommend")
def recommend_universities(profile: ProfileMatch):
    # Simple recommendation logic
    result = universities_data
    if profile.target_country and profile.target_country.lower() != "all":
        result = [u for u in result if u["country"].lower() == profile.target_country.lower()]
    
    result = sorted(result, key=lambda x: abs(x["avg_gpa_required"] - profile.gpa))
    
    # Add fake match %
    for u in result:
        diff = abs(u["avg_gpa_required"] - profile.gpa)
        match_pct = max(30, 99 - (diff * 20))
        u["match_percent"] = int(match_pct)
        
    return result[:5]

class ROIPayload(BaseModel):
    course_cost: float
    country: str
    course_type: str

@router.post("/roi/calculate")
def calculate_roi(payload: ROIPayload):
    # Mock salary data based on country
    salaries = {
        "USA": 8000000,
        "UK": 5000000,
        "Canada": 6000000,
        "Germany": 5500000,
        "Australia": 6500000
    }
    base_salary = salaries.get(payload.country, 5000000)
    
    yr1 = base_salary
    yr3 = base_salary * 1.2
    yr5 = base_salary * 1.5
    
    breakeven = payload.course_cost / (base_salary * 0.4) # Assuming 40% savings
    if breakeven < 1: breakeven = 1
    
    return {
        "year1_salary": yr1,
        "year3_salary": yr3,
        "year5_salary": yr5,
        "breakeven_years": round(breakeven, 1),
        "total_gain_10y": (yr1*2 + yr3*2 + yr5*6) - payload.course_cost
    }

class AdmissionPayload(BaseModel):
    gpa: float
    english_score: float
    work_exp: float
    sop_score: float

@router.post("/admission/predict")
def predict_admission(payload: AdmissionPayload):
    # Formula: (GPA/10 × 40) + (IELTS/9 × 30) + (work_exp/5 × 20) + (sop/5 × 10)
    work_norm = min(payload.work_exp / 5.0, 1.0)
    score = (payload.gpa / 10.0 * 40) + (payload.english_score / 9.0 * 30) + (work_norm * 20) + (payload.sop_score / 5.0 * 10)
    
    weakest = "GPA"
    if payload.english_score < 6.5: weakest = "IELTS"
    elif payload.sop_score < 3: weakest = "SOP"
    elif payload.work_exp < 1: weakest = "Work Experience"
    
    return {
        "probability": min(max(int(score), 10), 99),
        "tips": f"To improve your chances: Focus on improving your {weakest}."
    }
