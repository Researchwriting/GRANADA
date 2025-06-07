from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from typing import List
import io

from . import models, schemas, auth, database
from .database import SessionLocal, engine
from fpdf import FPDF
from docx import Document

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="GRANADA")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed = auth.get_password_hash(user.password)
    user_obj = models.User(username=user.username, email=user.email, hashed_password=hashed)
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return {"id": user_obj.id, "username": user_obj.username}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/proposal", response_model=schemas.Proposal)
def generate_proposal(data: schemas.ProposalCreate, token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.decode_token(token)
    user_id = int(payload.get("sub"))
    content = f"Proposal for {data.topic}. Objectives: {data.objectives}. SDGs: {', '.join(data.sdgs)}. (Generated text...)"
    proposal = models.Proposal(user_id=user_id, topic=data.topic, content=content)
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


@app.post("/donor_calls", response_model=schemas.DonorCall)
def create_donor_call(call: schemas.DonorCallCreate, db: Session = Depends(get_db)):
    call_obj = models.DonorCall(title=call.title, description=call.description,
                                sdg_tags=','.join(call.sdg_tags), keywords=','.join(call.keywords))
    db.add(call_obj)
    db.commit()
    db.refresh(call_obj)
    return schemas.DonorCall(id=call_obj.id, title=call_obj.title, description=call_obj.description,
                              sdg_tags=call.sdg_tags, keywords=call.keywords)


@app.get("/donor_calls", response_model=List[schemas.DonorCall])
def list_calls(db: Session = Depends(get_db)):
    calls = db.query(models.DonorCall).all()
    result = []
    for c in calls:
        result.append(schemas.DonorCall(id=c.id, title=c.title, description=c.description,
                                        sdg_tags=c.sdg_tags.split(','), keywords=c.keywords.split(',')))
    return result


@app.post("/match_donors")
def match_donors(data: schemas.ProposalCreate, db: Session = Depends(get_db)):
    matches = []
    calls = db.query(models.DonorCall).all()
    for c in calls:
        tags = c.sdg_tags.split(',') if c.sdg_tags else []
        if set(tags) & set(data.sdgs):
            matches.append({"id": c.id, "title": c.title})
    return {"matches": matches}


@app.post("/logframe")
def logframe(data: schemas.ProposalCreate):
    table = [
        {"objective": obj.strip(), "output": f"Output of {obj.strip()}", "outcome": f"Outcome of {obj.strip()}"}
        for obj in data.objectives.split(',')
    ]
    return {"logframe": table}


@app.post("/budget")
def budget():
    sample = [
        {"item": "Personnel", "amount": 10000},
        {"item": "Equipment", "amount": 5000},
        {"item": "Travel", "amount": 2000},
    ]
    return {"budget": sample}


@app.get("/export/{proposal_id}")
def export(proposal_id: int, format: str = "pdf", token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.decode_token(token)
    _ = payload.get("sub")  # Not used further
    proposal = db.query(models.Proposal).filter(models.Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    if format == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in proposal.content.split('\n'):
            pdf.multi_cell(0, 10, line)
        pdf_bytes = pdf.output(dest="S").encode('latin-1')
        return FileResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", filename="proposal.pdf")
    else:
        doc = Document()
        doc.add_paragraph(proposal.content)
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        return FileResponse(buf, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename="proposal.docx")
