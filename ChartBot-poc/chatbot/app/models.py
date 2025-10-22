from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    lan_id = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Project(Base):
    __tablename__ = "projects"
    
    project_id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ADGroup(Base):
    __tablename__ = "ad_groups"
    
    ad_group_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    ad_group_name = Column(String(200), nullable=False)
    approver_email = Column(String(100))
    approver_lan_id = Column(String(50), nullable=False)
    is_access_group = Column(Boolean, default=True)
    
    project = relationship("Project")

class UserProjectAccess(Base):
    __tablename__ = "user_project_access"
    
    access_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    access_type = Column(String(20))
    effective_from = Column(DateTime(timezone=True), server_default=func.now())
    effective_to = Column(DateTime(timezone=True))
    requested_by = Column(String(100))
    status = Column(String(20), default="ACTIVE")
    
    user = relationship("User")
    project = relationship("Project")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    log_id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String(50))
    user_lan_id = Column(String(50))
    project_code = Column(String(50))
    ad_groups = Column(Text)
    performed_by = Column(String(100))
    performed_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20))