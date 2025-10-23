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

class UserAdGroupAccess(Base):
    __tablename__ = "useradgroupaccess"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    adgroup_id = Column(Integer, ForeignKey("adgroups.adgroup_id"), primary_key=True)
    access_granted = Column(Boolean, default=True)
    grant_date = Column(DateTime(timezone=True), server_default=func.now())
    revoke_date = Column(DateTime(timezone=True))

    user = relationship("User")
    ad_group = relationship("AdGroup")

class AdGroupAccessRequest(Base):
    __tablename__ = "adgroupaccessrequests"

    request_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    adgroup_id = Column(Integer, ForeignKey("adgroups.adgroup_id"), nullable=False)
    request_type = Column(String(20), nullable=False)  # grant, revoke
    request_source = Column(String(20), default="chatbot")  # chatbot, bappas, admin
    request_status = Column(String(20), default="pending")  # pending, approved, rejected, cancelled
    approver_lanid = Column(String(50))
    approver_email = Column(String(255))
    requester_lanid = Column(String(50))
    request_date = Column(DateTime(timezone=True), server_default=func.now())
    decision_date = Column(DateTime(timezone=True))
    comments = Column(Text)

    user = relationship("User")
    ad_group = relationship("AdGroup")

class AccessHistory(Base):
    __tablename__ = "accesshistory"

    history_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    adgroup_id = Column(Integer, ForeignKey("adgroups.adgroup_id"))
    action = Column(String(20), nullable=False)  # grant, revoke, request, approval
    action_date = Column(DateTime(timezone=True), server_default=func.now())
    action_by = Column(String(50))  # LAN ID or system
    comments = Column(Text)

    user = relationship("User")
    ad_group = relationship("AdGroup")

class SystemApprover(Base):
    __tablename__ = "systemapprovers"

    approver_id = Column(Integer, primary_key=True, index=True)
    lan_id = Column(String(50), unique=True)
    full_name = Column(String(255))
    email = Column(String(255))
    role = Column(String(20), default="approver")  # approver, admin, hr
    is_active = Column(Boolean, default=True)

class NotificationQueue(Base):
    __tablename__ = "notificationqueue"

    notification_id = Column(Integer, primary_key=True, index=True)
    recipient_email = Column(String(255))
    recipient_lanid = Column(String(50))
    message_title = Column(String(255))
    message_body = Column(Text)
    status = Column(String(20), default="pending")  # pending, sent, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True))