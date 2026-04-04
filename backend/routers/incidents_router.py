from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import new, Person
from schemas import newCreate, newResponse, PublicnewResponse
from auth import get_current_user
import uuid

router = APIRouter()

@router.get("/public", response_model=List[PublicnewResponse])
def get_public_news(db: Session = Depends(get_db)):
    """Public endpoint - no authentication required"""
    news = db.query(new).all()
    return [{"registration_number": inc.registration_number, "location": inc.location} 
            for inc in news]

@router.get("/", response_model=List[newResponse])
def get_all_news(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all news - requires authentication"""
    news = db.query(new).all()
    
    # Convert to response format with involvedPersons as list of IDs
    result = []
    for inc in news:
        new_dict = {
            "id": inc.id,
            "registration_number": inc.registration_number,
            "type": inc.type,
            "description": inc.description,
            "location": inc.location,
            "date": inc.date,
            "severity": inc.severity.value,
            "involvedPersons": [p.id for p in inc.involved_persons]
        }
        result.append(new_dict)
    
    return result

@router.post("/", response_model=newResponse)
def create_new(
    new: newCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new new - requires authentication"""
    new_new = new(
        id=f"inc-{uuid.uuid4()}",
        registration_number=f"RN{uuid.uuid4().hex[:6].upper()}",
        type=new.type,
        description=new.description,
        location=new.location,
        severity=new.severity,
        date=datetime.utcnow()
    )
    
    # Add involved persons
    for person_id in new.involvedPersons:
        person = db.query(Person).filter(Person.id == person_id).first()
        if person:
            new_new.involved_persons.append(person)
    
    db.add(new_new)
    db.commit()
    db.refresh(new_new)
    
    return {
        "id": new_new.id,
        "registration_number": new_new.registration_number,
        "type": new_new.type,
        "description": new_new.description,
        "location": new_new.location,
        "date": new_new.date,
        "severity": new_new.severity.value,
        "involvedPersons": [p.id for p in new_new.involved_persons]
    }

@router.get("/by-person/{person_id}", response_model=List[newResponse])
def get_news_by_person(
    person_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all news involving a specific person"""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    result = []
    for inc in person.news:
        new_dict = {
            "id": inc.id,
            "registration_number": inc.registration_number,
            "type": inc.type,
            "description": inc.description,
            "location": inc.location,
            "date": inc.date,
            "severity": inc.severity.value,
            "involvedPersons": [p.id for p in inc.involved_persons]
        }
        result.append(new_dict)
    
    return result