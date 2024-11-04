from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlmodel import select, Session
from typing import List, Optional, Tuple

from app.db import get_db
from app.models import Location, Organisation, CreateOrganisation, CreateLocation, LocationResponse

router = APIRouter()

@router.post("/create", response_model=Organisation)
def create_organisation(create_organisation: CreateOrganisation, session: Session = Depends(get_db)) -> Organisation:
    """Create an organisation."""
    organisation = Organisation(name=create_organisation.name)
    session.add(organisation)
    session.commit()
    session.refresh(organisation)
    return organisation

@router.get("/", response_model=list[Organisation])
def get_organisations(session: Session = Depends(get_db)) -> list[Organisation]:
    """
    Get all organisations.
    """
    organisations = session.exec(select(Organisation)).all()
    return organisations

@router.get("/{organisation_id}", response_model=Organisation)
def get_organisation(organisation_id: int, session: Session = Depends(get_db)) -> Organisation:
    """
    Get an organisation by id.
    """
    organisation = session.get(Organisation, organisation_id)
    return organisation

@router.post("/create/location", response_model=Location)
def create_location(create_location: CreateLocation, session: Session = Depends(get_db)) -> Location:
    """Create a location for an organisation."""
    # Create and save the location
    location = Location(
        organisation_id=create_location.organisation_id,
        location_name=create_location.location_name,
        longitude=create_location.longitude,
        latitude=create_location.latitude
    )
    session.add(location)
    session.commit()
    session.refresh(location)
    return location

@router.get("/{organisation_id}/locations", response_model=List[LocationResponse])
def get_organisation_locations(
    organisation_id: int,
    session: Session = Depends(get_db),
    bounding_box: Optional[Tuple[float, float, float, float]] = Query(None)
):
    """Get all locations for a specified organisation, optionally filtered by a bounding box."""
    query = select(Location).where(Location.organisation_id == organisation_id)

    # Apply bounding box filter if provided
    if bounding_box:
        min_long, min_lat, max_long, max_lat = bounding_box
        query = query.where(
            (Location.longitude >= min_long) & 
            (Location.longitude <= max_long) &
            (Location.latitude >= min_lat) & 
            (Location.latitude <= max_lat)
        )

    locations = session.exec(query).all()

    return locations

# @router.get("/{organisation_id}/locations")
# def get_organisation_locations(organisation_id: int, session: Session = Depends(get_db)):
#     location_ids = session.exec(select(Location.id).where(Location.organisation_id==organisation_id)).all()
#     result = []
#     for location_id in location_ids:
#         location = session.exec(select(Location).where(Location.id == location_id)).one()
#         result.append({"location_name": location.location_name, "location_longitude": location.longitude, "location_latitude": location.latitude })
#     return result
