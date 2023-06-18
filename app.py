from fastapi import FastAPI, Depends, HTTPException, Header, Request, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Configure SQLAlchemy
SQLALCHEMY_DATABASE_URL = 'sqlite:///' + os.getenv('DB')
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class FoodData(Base):
    __tablename__ = 'food_data'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    category = Column(String(200))


Base.metadata.create_all(bind=engine)


class FoodDataRequest(BaseModel):
    name: str
    category: str

def validate_custom_header(token: str = Header(...)):
    print(token)
    if token != os.getenv('TOKEN'):
        raise HTTPException(status_code=400, detail="Invalid custom header value")
    return token

@app.post('/food')
async def save_food(food_data: FoodDataRequest, token: str = Depends(validate_custom_header)):
    
    db = SessionLocal()
    new_food_data = FoodData(name=food_data.name, category=food_data.category)
    db.add(new_food_data)
    db.commit()
    db.close()
    return {'message': 'Food data saved successfully'}

@app.exception_handler(status.HTTP_422_UNPROCESSABLE_ENTITY)
async def error_handler(request: Request, exc: Exception):
    # Log the error details
    print(exc.errors(), exc.body)

    # Return a custom error response
    return {"message": "Internal Server Error"}