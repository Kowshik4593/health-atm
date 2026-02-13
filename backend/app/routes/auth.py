import random
import string
import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
# Import the shared supabase client
from app.supabase_client import supabase 
from app.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

# --- Request Models ---
class CreatePatientRequest(BaseModel):
    email: str
    password: str
    full_name: str
    phone: str
    dob: str
    gender: str

# --------------------------
# OPERATOR: WALK-IN PATIENT CREATION
# --------------------------
@router.post("/create-patient")
def create_patient(data: CreatePatientRequest, user=Depends(get_current_user)):
    # SECURE: Only Operators can create auto-verified patients
    if user.role != "operator":
        raise HTTPException(status_code=403, detail="Only operators can create walk-in patients")

    try:
        print(f"Creating patient: {data.email}")
        
        # Create user with email_confirm=True (Auto-verify)
        auth_res = supabase.auth.admin.create_user({
            "email": data.email,
            "password": data.password,
            "email_confirm": True,
            "user_metadata": {
                "full_name": data.full_name,
                "role": "patient"
            }
        })
        
        new_user = auth_res.user if hasattr(auth_res, "user") else auth_res
        if not new_user:
             raise Exception("Failed to create auth user")
             
        user_id = new_user.id if hasattr(new_user, "id") else new_user["id"]

        # Insert into Profiles
        profile_data = {
            "id": user_id,
            "full_name": data.full_name,
            "phone": data.phone,
            "dob": data.dob,
            "gender": data.gender,
            "role": "patient",
            "country": "India",
            "state": "Unknown",
            "city": "Unknown",
            "postal_code": "000000"
        }
        
        supabase.table("profiles").insert(profile_data).execute()
        
        return {"status": "created", "user_id": user_id}

    except Exception as e:
        print(f"Create Patient Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# --------------------------
# OPERATOR: FETCH PROFILE (Admin Bypass)
# --------------------------
@router.get("/profile/{user_id}")
def get_profile(user_id: str, user=Depends(get_current_user)):
    # SECURE: Only Operators/Doctors can peek at other profiles via backend
    if user.role not in ("operator", "doctor"):
        # Allow user to read their own profile
        if not (user.role == "patient" and user.id == user_id):
            raise HTTPException(status_code=403, detail="Forbidden")

    try:
        res = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Profile not found")
        return res.data[0]
    except Exception as e:
        print(f"Get Profile Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))