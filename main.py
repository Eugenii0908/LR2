from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json


class Student(BaseModel):
    name: str
    group: str
    age: int
    average_score: int | None = None

class StudentOut(Student):
    id: int

db_file = "db.json"
try:
    with open(db_file, 'r') as db:
        students = [StudentOut(**item) for item in json.load(db)]
except FileNotFoundError:
    students = []

def save_db():
    with open(db_file, 'w') as db:
        json.dump([s.model_dump() for s in students], db, indent = 4)


app = FastAPI()

@app.post("/students")
def post(student: Student):
    new_id = 0
    for s in students:
        new_id = max(new_id, s.id)
    new_id = new_id + 1
    new_student = StudentOut(id = new_id, **student.model_dump())
    students.append(new_student)
    save_db()
    return student

@app.get("/students")
def get():
    return students

@app.get("/student")
def get(student_id: int):
    for s in students:
        if (s.id == student_id):
            return s
    raise HTTPException(status_code=404, detail="Student not found")

@app.delete("/students")
def delete(student_id: int):
    for s in students:
        if (s.id == student_id):
            students.remove(s)
            save_db()
            return students
    raise HTTPException(status_code=404, detail="Student not found")