from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.tables import Address
from app.schemas.address_schemas import AddressCreate, AddressUpdate

async def create_address(db: Session, current_user, address_data: AddressCreate):
    # If this address is set as default, update all others to not be default
    if address_data.is_default:
        db.query(Address).filter(Address.user_id == current_user.id).update({"is_default": False})
        
    new_address = Address(
        user_id=current_user.id,
        address_line1=address_data.address_line1,
        address_line2=address_data.address_line2,
        city=address_data.city,
        state=address_data.state,
        country=address_data.country,
        postal_code=address_data.postal_code,
        latitude=address_data.latitude,
        longitude=address_data.longitude,
        is_default=address_data.is_default
    )
    
    try:
        db.add(new_address)
        db.commit()
        db.refresh(new_address)
        return {
            "message": "Address created successfully",
            "address": {
                "id": new_address.id,
                "address_line1": new_address.address_line1,
                "city": new_address.city,
                "is_default": new_address.is_default
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def get_addresses(db: Session, current_user):
    addresses = db.query(Address).filter(Address.user_id == current_user.id).all()
    return [
        {
            "id": a.id,
            "address_line1": a.address_line1,
            "address_line2": a.address_line2,
            "city": a.city,
            "state": a.state,
            "country": a.country,
            "postal_code": a.postal_code,
            "latitude": a.latitude,
            "longitude": a.longitude,
            "is_default": a.is_default
        } for a in addresses
    ]

async def update_address(db: Session, current_user, address_id: int, address_data: AddressUpdate):
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == current_user.id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
        
    if address_data.is_default is True:
        db.query(Address).filter(Address.user_id == current_user.id).update({"is_default": False})
        
    # Update fields
    for field, value in address_data.model_dump(exclude_unset=True).items():
        setattr(address, field, value)
        
    try:
        db.commit()
        db.refresh(address)
        return {"message": "Address updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def delete_address(db: Session, current_user, address_id: int):
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == current_user.id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
        
    try:
        db.delete(address)
        db.commit()
        return {"message": "Address deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
