from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db

router = APIRouter()

class BookingCreate(BaseModel):
    patient_name: str
    phone: str
    notes: str = ""
    time: str
    booking_date: str

async def init_db(db: AsyncSession):
    await db.execute(text("""
        CREATE TABLE IF NOT EXISTS dashboard_bookings (
            id TEXT PRIMARY KEY,
            patient_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            notes TEXT,
            time TEXT NOT NULL,
            date_created TEXT,
            booking_date TEXT
        )
    """))
    # Add columns if they don't exist for existing tables
    for col in ["date_created", "booking_date"]:
        try:
            await db.execute(text(f"ALTER TABLE dashboard_bookings ADD COLUMN {col} TEXT"))
            await db.commit()
        except Exception:
            pass
    await db.commit()

@router.get("/")
async def get_bookings(date: str = None, db: AsyncSession = Depends(get_db)):
    await init_db(db)
    query = "SELECT * FROM dashboard_bookings"
    params = {}
    if date:
        query += " WHERE booking_date = :date"
        params["date"] = date
    result = await db.execute(text(query), params)
    return [dict(row) for row in result.mappings().all()]

@router.post("/")
async def create_booking(booking: BookingCreate, db: AsyncSession = Depends(get_db)):
    await init_db(db)
    booking_id = "appt-" + booking.time.replace(":", "-") + "-" + booking.booking_date
    
    result = await db.execute(text("SELECT id FROM dashboard_bookings WHERE id = :id"), {"id": booking_id})
    if result.fetchone():
        raise HTTPException(status_code=400, detail="Slot already booked for this date")
        
    await db.execute(text("""
        INSERT INTO dashboard_bookings (id, patient_name, phone, notes, time, date_created, booking_date)
        VALUES (:id, :name, :phone, :notes, :time, :date_created, :booking_date)
    """), {
        "id": booking_id,
        "name": booking.patient_name,
        "phone": booking.phone,
        "notes": booking.notes,
        "time": booking.time,
        "date_created": booking.time, 
        "booking_date": booking.booking_date
    })
    await db.commit()
    return {"message": "Booking created successfully"}

@router.delete("/{booking_id}")
async def delete_booking(booking_id: str, db: AsyncSession = Depends(get_db)):
    await init_db(db)
    await db.execute(text("DELETE FROM dashboard_bookings WHERE id = :id"), {"id": booking_id})
    await db.commit()
    return {"message": "Booking deleted successfully"}
