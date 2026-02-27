"""
数据模型定义
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'assessments.db')
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AssessmentTask(Base):
    """评估任务"""
    __tablename__ = "assessment_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    template_id = Column(String(50), nullable=False)  # 使用的标准模板 ID
    organization = Column(String(200))  # 被评估组织
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    status = Column(String(20), default="draft")  # draft, in_progress, completed
    total_score = Column(Float, default=0.0)
    compliance_rate = Column(Float, default=0.0)
    
    items = relationship("AssessmentItem", back_populates="task", cascade="all, delete-orphan")


class AssessmentItem(Base):
    """评估项（每个控制项的评估结果）"""
    __tablename__ = "assessment_items"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("assessment_tasks.id"), nullable=False)
    template_item_id = Column(String(100), nullable=False)  # 模板中的项 ID
    dimension = Column(String(100))  # 所属维度
    control_item = Column(Text)  # 控制项内容
    level = Column(String(20))  # 等级/级别
    
    rating = Column(String(20))  # 评分：compliant, partial, non_compliant, not_applicable
    score = Column(Float, default=0.0)
    evidence = Column(Text)  # 证据描述
    remarks = Column(Text)  # 备注
    has_attachment = Column(Boolean, default=False)
    
    task = relationship("AssessmentTask", back_populates="items")


class StandardTemplate(Base):
    """标准模板"""
    __tablename__ = "standard_templates"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    standard_no = Column(String(50))  # 标准编号
    version = Column(String(20))
    description = Column(Text)
    dimensions = Column(JSON)  # 维度定义
    items = Column(JSON)  # 评估项列表
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)


def init_db():
    """初始化数据库"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    Base.metadata.create_all(bind=engine)
    
    # 初始化默认模板
    from templates import get_default_templates
    db = SessionLocal()
    try:
        default_templates = get_default_templates()
        for tpl in default_templates:
            existing = db.query(StandardTemplate).filter(StandardTemplate.id == tpl["id"]).first()
            if not existing:
                template = StandardTemplate(**tpl)
                db.add(template)
        db.commit()
    finally:
        db.close()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
