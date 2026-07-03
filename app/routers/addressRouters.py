from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.dataConfig import get_db
from app.core.getRole import get_current_user
from app.schemas.address_schemas import AddressCreate, AddressUpdate, AddressResponse
from app.services.addressServices import create_address, get_addresses, update_address, delete_address
from typing import List

router = APIRouter(
    prefix="/address",
    tags=["Address"]
)

@router.post("", response_model=dict)
async def add_address(
    address_data: AddressCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await create_address(db, current_user, address_data)

@router.get("", response_model=List[AddressResponse])
async def list_addresses(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await get_addresses(db, current_user)

@router.put("/{id}")
async def update_existing_address(
    id: int,
    address_data: AddressUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await update_address(db, current_user, id, address_data)

@router.delete("/{id}")
async def delete_existing_address(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await delete_address(db, current_user, id)
