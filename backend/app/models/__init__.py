from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

Base = declarative_base()

DATABASE_URL = "sqlite:///./assessment.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class AssessmentResult(str, enum.Enum):
    COMPLIANT = "符合"
    PARTIALLY_COMPLIANT = "部分符合"
    NON_COMPLIANT = "不符合"
    NOT_APPLICABLE = "不适用"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    templates = relationship("Template", back_populates="owner")
    tasks = relationship("AssessmentTask", back_populates="owner")


class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    file_path = Column(String(500))
    level = Column(String(50))  # 如：DSMM 二级、三级、四级
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="templates")
    clauses = relationship("Clause", back_populates="template", cascade="all, delete-orphan")


class Clause(Base):
    __tablename__ = "clauses"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    clause_number = Column(String(50))  # 条款编号
    clause_content = Column(Text, nullable=False)  # 条款内容
    requirement = Column(Text)  # 具体要求
    domain = Column(String(100))  # 能力域 (DSMM 专用)
    sub_domain = Column(String(100))  # 子能力域 (DSMM 专用)
    seq = Column(Integer)  # 序号 (DSMM 专用)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    template = relationship("Template", back_populates="clauses")
    results = relationship("AssessmentResultItem", back_populates="clause")


class AssessmentTask(Base):
    __tablename__ = "assessment_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(100), nullable=False)
    organization = Column(String(200))  # 评估组织
    system_name = Column(String(200))  # 评估系统
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    business_status = Column(Text)  # 业务现状
    total_score = Column(Float)  # 总分 (0-100)
    level = Column(String(20))  # 优秀/良好/合格/不合格
    status = Column(String(20), default="pending")  # pending, processing, completed
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    owner = relationship("User", back_populates="tasks")
    template = relationship("Template")
    results = relationship("AssessmentResultItem", back_populates="task", cascade="all, delete-orphan")


class AssessmentResultItem(Base):
    __tablename__ = "assessment_result_items"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("assessment_tasks.id"), nullable=False)
    clause_id = Column(Integer, ForeignKey("clauses.id"), nullable=False)
    result = Column(Enum(AssessmentResult))  # 符合/部分符合/不符合/不适用
    score = Column(Float)  # 1/0.6/0
    evidence = Column(Text)  # 评估依据
    comment = Column(Text)  # 评语
    created_at = Column(DateTime, default=datetime.utcnow)
    
    task = relationship("AssessmentTask", back_populates="results")
    clause = relationship("Clause", back_populates="results")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
