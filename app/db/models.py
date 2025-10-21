from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


# Enums
class UserType(str, enum.Enum):
    EMPLOYEE = "employee"
    VISITOR = "visitor"


class SpaceType(str, enum.Enum):
    DESK = "desk"
    OFFICE = "office"
    MEETING_ROOM = "meeting_room"


class BookingStatus(str, enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class CheckInStatus(str, enum.Enum):
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"


# Models
class User(Base):
    """Employee/User model"""
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)  # USR-001
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    building_id = Column(String(50), ForeignKey("buildings.id"))
    programme = Column(String(100))  # Programme 1A, 1B, etc.
    laptop_model = Column(String(200))
    laptop_asset_number = Column(String(100))
    photo_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    building = relationship("Building", back_populates="users")
    check_ins = relationship("CheckIn", back_populates="user")
    bookings = relationship("Booking", back_populates="user")
    laptop_records = relationship("LaptopRecord", back_populates="user")


class Visitor(Base):
    """Visitor model"""
    __tablename__ = "visitors"

    id = Column(String(50), primary_key=True, index=True)  # VIS-000001
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company = Column(String(200))
    mobile = Column(String(20), nullable=False)
    email = Column(String(255))
    photo_url = Column(String(500))

    # Visit details
    purpose = Column(String(20))  # EmployeeVisit or Other
    host_employee_id = Column(String(50), ForeignKey("users.id"))
    host_employee_name = Column(String(200))
    other_reason = Column(String(500))

    # Location
    building_id = Column(String(50), ForeignKey("buildings.id"))
    floor = Column(String(50))
    block = Column(String(50))

    # Security
    has_weapons = Column(Boolean, default=False)
    weapon_details = Column(Text)

    # Metadata
    device_id = Column(String(100))  # Kiosk device
    registered_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    host = relationship("User", foreign_keys=[host_employee_id])
    building = relationship("Building")
    check_ins = relationship("CheckIn", back_populates="visitor")


class Building(Base):
    """Building model"""
    __tablename__ = "buildings"

    id = Column(String(50), primary_key=True, index=True)  # BLDG-001
    name = Column(String(100), nullable=False)  # Building 41
    address = Column(String(500))
    total_floors = Column(Integer, default=1)
    total_blocks = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="building")
    floors = relationship("Floor", back_populates="building", cascade="all, delete-orphan")
    spaces = relationship("Space", back_populates="building")


class Floor(Base):
    """Floor model - custom floor names"""
    __tablename__ = "floors"

    id = Column(String(50), primary_key=True, index=True)  # FLR-001
    building_id = Column(String(50), ForeignKey("buildings.id"), nullable=False)
    name = Column(String(100), nullable=False)  # Ground Floor, First Floor, etc.
    order = Column(Integer, default=0)  # For sorting
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    building = relationship("Building", back_populates="floors")
    blocks = relationship("Block", back_populates="floor", cascade="all, delete-orphan")


class Block(Base):
    """Block model - custom block names per floor"""
    __tablename__ = "blocks"

    id = Column(String(50), primary_key=True, index=True)  # BLK-001
    floor_id = Column(String(50), ForeignKey("floors.id"), nullable=False)
    name = Column(String(100), nullable=False)  # Block A, North Wing, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    floor = relationship("Floor", back_populates="blocks")


class Space(Base):
    """Space model - Desks, Offices, Meeting Rooms"""
    __tablename__ = "spaces"

    id = Column(String(50), primary_key=True, index=True)  # SPC-001
    name = Column(String(200), nullable=False)
    type = Column(SQLEnum(SpaceType), nullable=False)
    building_id = Column(String(50), ForeignKey("buildings.id"), nullable=False)
    floor = Column(String(100))
    block = Column(String(100))
    capacity = Column(Integer, default=1)
    description = Column(Text)
    image_url = Column(String(500))

    # Amenities (stored as JSON-like string or separate table)
    has_wifi = Column(Boolean, default=False)
    has_monitor = Column(Boolean, default=False)
    has_coffee = Column(Boolean, default=False)
    has_video_conf = Column(Boolean, default=False)
    has_projector = Column(Boolean, default=False)
    has_whiteboard = Column(Boolean, default=False)
    has_power = Column(Boolean, default=False)
    has_standing_desk = Column(Boolean, default=False)
    has_conference_phone = Column(Boolean, default=False)

    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    building = relationship("Building", back_populates="spaces")
    bookings = relationship("Booking", back_populates="space")


class Booking(Base):
    """Booking model"""
    __tablename__ = "bookings"

    id = Column(String(50), primary_key=True, index=True)  # BK-001
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    space_id = Column(String(50), ForeignKey("spaces.id"), nullable=False)

    booking_date = Column(DateTime, nullable=False)
    start_time = Column(String(10))  # "09:00"
    end_time = Column(String(10))    # "17:00"

    status = Column(SQLEnum(BookingStatus), default=BookingStatus.CONFIRMED)

    # Meeting room specific
    guest_emails = Column(Text)  # Comma-separated
    notify_guests = Column(Boolean, default=False)

    # QR code
    qr_code_url = Column(String(500))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="bookings")
    space = relationship("Space", back_populates="bookings")


class CheckIn(Base):
    """Check-in/Check-out records"""
    __tablename__ = "checkins"

    id = Column(String(50), primary_key=True, index=True)  # CHK-001

    # Can be either user or visitor
    user_id = Column(String(50), ForeignKey("users.id"), nullable=True)
    visitor_id = Column(String(50), ForeignKey("visitors.id"), nullable=True)
    user_type = Column(SQLEnum(UserType), nullable=False)

    # Location
    building_id = Column(String(50), ForeignKey("buildings.id"))
    floor = Column(String(100))
    block = Column(String(100))

    # Laptop info (for employees)
    laptop_model = Column(String(200))
    laptop_asset_number = Column(String(100))

    # Time tracking
    check_in_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    check_out_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    status = Column(SQLEnum(CheckInStatus), default=CheckInStatus.CHECKED_IN)

    # QR code data
    qr_code_data = Column(String(500))

    # Relationships
    user = relationship("User", back_populates="check_ins")
    visitor = relationship("Visitor", back_populates="check_ins")
    building = relationship("Building")


class LaptopRecord(Base):
    """Laptop tracking records"""
    __tablename__ = "laptop_records"

    id = Column(String(50), primary_key=True, index=True)  # LAP-001
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)

    # Registered laptop (from user profile)
    registered_laptop = Column(String(200))
    registered_asset_number = Column(String(100))

    # Actually checked in with
    checked_in_laptop = Column(String(200))
    checked_in_asset_number = Column(String(100))

    # Match status
    is_match = Column(Boolean, default=True)

    # Location
    building_id = Column(String(50), ForeignKey("buildings.id"))
    floor = Column(String(100))
    block = Column(String(100))

    # Time tracking
    check_in_date = Column(DateTime, nullable=False)
    check_in_time = Column(String(10))
    check_out_date = Column(DateTime, nullable=True)
    check_out_time = Column(String(10), nullable=True)
    duration = Column(String(50), nullable=True)

    # Security verification
    checked_out_by_officer = Column(String(200))
    officer_badge = Column(String(50))

    status = Column(SQLEnum(CheckInStatus), default=CheckInStatus.CHECKED_IN)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="laptop_records")
    building = relationship("Building")


class SecurityOfficer(Base):
    """Security officer model"""
    __tablename__ = "security_officers"

    id = Column(String(50), primary_key=True, index=True)  # SEC-001
    badge_number = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    hashed_pin = Column(String(255), nullable=False)  # 6-digit PIN hashed
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AdminUser(Base):
    """Admin user model"""
    __tablename__ = "admin_users"

    id = Column(String(50), primary_key=True, index=True)  # ADM-001
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(50), default="admin")  # admin, super_admin, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
