from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Float, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Time, CheckConstraint
import uuid
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


# Enums
class UserType(str, enum.Enum):
    EMPLOYEE = "employee"
    VISITOR = "visitor"



# New SpaceType Enum
class SpaceType(str, enum.Enum):
    DESK = "DESK"
    OFFICE = "OFFICE"
    ROOM = "ROOM"


class BookingStatus(str, enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class CheckInStatus(str, enum.Enum):
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"


# Models

# New Programme model
class Programme(Base):
    __tablename__ = "programmes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)


class User(Base):
    """Employee/User model"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="SET NULL"), nullable=True)
    programme_id = Column(UUID(as_uuid=True), ForeignKey("programmes.id", ondelete="SET NULL"), nullable=True)
    laptop_model = Column(String(200))
    laptop_asset_number = Column(String(100))
    photo_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    building = relationship("Building")
    programme = relationship("Programme")
    check_ins = relationship("CheckIn", back_populates="user")
    bookings = relationship("Booking", back_populates="user")
    laptop_records = relationship("LaptopRecord", back_populates="user")


class Visitor(Base):
    """Visitor model"""
    __tablename__ = "visitors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company = Column(String(200))
    mobile = Column(String(20), nullable=False)
    email = Column(String(255))
    photo_url = Column(String(500))

    # Visit details
    purpose = Column(String(20))  # EmployeeVisit or Other
    host_employee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    host_employee_name = Column(String(200))
    other_reason = Column(String(500))

    # Location
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="SET NULL"), nullable=True)
    floor = Column(String(50))
    block = Column(String(50))

    # Security
    has_weapons = Column(Boolean, default=False)
    weapon_details = Column(Text)

    # Metadata
    device_id = Column(String(100))  # Kiosk device
    registered_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    host = relationship("User", foreign_keys=[host_employee_id])
    building = relationship("Building")
    check_ins = relationship("CheckIn", back_populates="visitor")



# New Building model
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Building(Base):
    __tablename__ = "buildings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    building_code = Column(String, unique=True, nullable=False, index=True)  # e.g., BLD-001
    name = Column(String, nullable=False)  # e.g., Building 41
    address = Column(String, nullable=False)  # e.g., 123 Innovation Drive, Pretoria
    floors_count = Column(Integer, nullable=False)  # Required, >= 0
    blocks_count = Column(Integer, nullable=False)  # Required, >= 0
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    spaces = relationship("Space", back_populates="building", cascade="all, delete-orphan")
    floors = relationship("Floor", back_populates="building", cascade="all, delete-orphan")
    blocks = relationship("Block", back_populates="building", cascade="all, delete-orphan")

    # total_spaces is computed property (read-only, not a DB column)
    @property
    def total_spaces(self):
        return sum(space.quantity for space in self.spaces) if self.spaces else 0



# New Floor model
class Floor(Base):
    __tablename__ = "floors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)
    floor_index = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint: (building_id, floor_index)
    __table_args__ = (
        UniqueConstraint('building_id', 'floor_index', name='uq_building_floor_index'),
    )

    # Relationships
    building = relationship("Building", back_populates="floors")





# New Block model
class Block(Base):
    __tablename__ = "blocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)
    block_label = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint: (building_id, block_label)
    __table_args__ = (
        UniqueConstraint('building_id', 'block_label', name='uq_building_block_label'),
    )

    # Relationships
    building = relationship("Building", back_populates="blocks")



# New Space model
from sqlalchemy import UniqueConstraint
class Space(Base):
    __tablename__ = "spaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False)
    type = Column(SQLEnum(SpaceType), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint: (building_id, type)
    __table_args__ = (
        UniqueConstraint('building_id', 'type', name='uq_building_space_type'),
    )

    # Relationships
    building = relationship("Building", back_populates="spaces")


class Booking(Base):
    """Booking model"""
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    space_id = Column(UUID(as_uuid=True), ForeignKey("spaces.id", ondelete="CASCADE"), nullable=False)

    booking_date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(Time(timezone=True), nullable=False)
    end_time = Column(Time(timezone=True), nullable=False)

    status = Column(SQLEnum(BookingStatus), default=BookingStatus.CONFIRMED)

    # Meeting room specific
    guest_emails = Column(Text)  # Comma-separated
    notify_guests = Column(Boolean, default=False)

    # QR code
    qr_code_url = Column(String(500))

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (
        CheckConstraint('start_time < end_time', name='ck_booking_start_before_end'),
    )

    # Relationships
    user = relationship("User", back_populates="bookings")


class CheckIn(Base):
    """Check-in/Check-out records"""
    __tablename__ = "checkins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Can be either user or visitor
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    visitor_id = Column(UUID(as_uuid=True), ForeignKey("visitors.id", ondelete="SET NULL"), nullable=True)
    user_type = Column(SQLEnum(UserType), nullable=False)

    # Location
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="SET NULL"), nullable=True)
    floor = Column(String(100))
    block = Column(String(100))

    __table_args__ = (
        # Enforce exactly one of user_id or visitor_id is set (XOR)
        CheckConstraint(
            '((user_id IS NOT NULL)::integer + (visitor_id IS NOT NULL)::integer) = 1',
            name='ck_checkin_user_xor_visitor'
        ),
    )

    # Laptop info (for employees)
    laptop_model = Column(String(200))
    laptop_asset_number = Column(String(100))

    # Time tracking
    check_in_time = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    check_out_time = Column(DateTime(timezone=True), nullable=True)
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Registered laptop (from user profile)
    registered_laptop = Column(String(200))
    registered_asset_number = Column(String(100))

    # Actually checked in with
    checked_in_laptop = Column(String(200))
    checked_in_asset_number = Column(String(100))

    # Match status
    is_match = Column(Boolean, default=True)

    # Location
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id", ondelete="SET NULL"), nullable=True)
    floor = Column(String(100))
    block = Column(String(100))

    # Time tracking
    check_in_date = Column(DateTime(timezone=True), nullable=False)
    check_in_time = Column(Time(timezone=True), nullable=True)
    check_out_date = Column(DateTime(timezone=True), nullable=True)
    check_out_time = Column(Time(timezone=True), nullable=True)
    duration = Column(String(50), nullable=True)

    # Security verification
    checked_out_by_officer = Column(String(200))
    officer_badge = Column(String(50))

    status = Column(SQLEnum(CheckInStatus), default=CheckInStatus.CHECKED_IN)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="laptop_records")
    building = relationship("Building")


class SecurityOfficer(Base):
    """Security officer model"""
    __tablename__ = "security_officers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    badge_number = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    hashed_pin = Column(String(255), nullable=False)  # 6-digit PIN hashed
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class AdminUser(Base):
    """Admin user model"""
    __tablename__ = "admin_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(50), default="admin")  # admin, super_admin, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
