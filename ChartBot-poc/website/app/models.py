from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date, func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    lan_id = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AdGroup(Base):
    __tablename__ = "adgroups"

    adgroup_id = Column(Integer, primary_key=True, index=True)
    adgroup_name = Column(String(255), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    approver_emails = Column(Text)
    approver_lanids = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project")

class UserProjectAssignment(Base):
    __tablename__ = "userprojectassignment"

    assignment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    start_date = Column(Date, server_default=func.current_date())
    end_date = Column(Date)
    is_current = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    project = relationship("Project")