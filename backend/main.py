"""
标准自评估系统 - FastAPI 后端
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import json
import os

from models import (
    AssessmentTask, AssessmentItem, StandardTemplate,
    init_db, get_db, engine, Base
)
from templates import get_default_templates, RATING_SCORES, RATING_LABELS

app = FastAPI(
    title="标准自评估系统 API",
    description="网络安全、数据安全标准自评估平台",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    init_db()


# ============ Pydantic 模型 ============

class AssessmentTaskCreate(BaseModel):
    name: str
    template_id: str
    organization: Optional[str] = None


class AssessmentTaskUpdate(BaseModel):
    name: Optional[str] = None
    organization: Optional[str] = None
    status: Optional[str] = None


class AssessmentItemUpdate(BaseModel):
    rating: str
    evidence: Optional[str] = None
    remarks: Optional[str] = None


class AssessmentResult(BaseModel):
    task_id: int
    total_items: int
    completed_items: int
    total_score: float
    max_score: float
    compliance_rate: float
    dimension_scores: dict
    level_distribution: dict


# ============ 模板接口 ============

@app.get("/api/templates", response_model=List[dict])
def get_templates(db: Session = Depends(get_db)):
    """获取所有标准模板"""
    templates = db.query(StandardTemplate).filter(StandardTemplate.is_active == True).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "standard_no": t.standard_no,
            "version": t.version,
            "description": t.description,
            "dimensions": t.dimensions,
            "item_count": len(t.items) if t.items else 0
        }
        for t in templates
    ]


@app.get("/api/templates/{template_id}")
def get_template(template_id: str, db: Session = Depends(get_db)):
    """获取模板详情"""
    template = db.query(StandardTemplate).filter(StandardTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return {
        "id": template.id,
        "name": template.name,
        "standard_no": template.standard_no,
        "version": template.version,
        "description": template.description,
        "dimensions": template.dimensions,
        "items": template.items
    }


# ============ 评估任务接口 ============

@app.get("/api/tasks", response_model=List[dict])
def get_tasks(db: Session = Depends(get_db)):
    """获取所有评估任务"""
    tasks = db.query(AssessmentTask).order_by(AssessmentTask.updated_at.desc()).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "template_id": t.template_id,
            "organization": t.organization,
            "status": t.status,
            "compliance_rate": t.compliance_rate,
            "created_at": t.created_at.isoformat(),
            "updated_at": t.updated_at.isoformat()
        }
        for t in tasks
    ]


@app.post("/api/tasks")
def create_task(task: AssessmentTaskCreate, db: Session = Depends(get_db)):
    """创建新的评估任务"""
    # 验证模板存在
    template = db.query(StandardTemplate).filter(StandardTemplate.id == task.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    db_task = AssessmentTask(
        name=task.name,
        template_id=task.template_id,
        organization=task.organization,
        status="draft"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # 初始化评估项
    if template.items:
        for item in template.items:
            db_item = AssessmentItem(
                task_id=db_task.id,
                template_item_id=item["id"],
                dimension=item.get("dimension", ""),
                control_item=item.get("content", ""),
                level=item.get("level", ""),
                rating="not_started"
            )
            db.add(db_item)
        db.commit()
    
    return {"id": db_task.id, "message": "评估任务创建成功"}


@app.get("/api/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    """获取任务详情"""
    task = db.query(AssessmentTask).filter(AssessmentTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    template = db.query(StandardTemplate).filter(StandardTemplate.id == task.template_id).first()
    items = db.query(AssessmentItem).filter(AssessmentItem.task_id == task_id).all()
    
    return {
        "id": task.id,
        "name": task.name,
        "template_id": task.template_id,
        "template_name": template.name if template else task.template_id,
        "organization": task.organization,
        "status": task.status,
        "compliance_rate": task.compliance_rate,
        "total_score": task.total_score,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "items": [
            {
                "id": i.id,
                "template_item_id": i.template_item_id,
                "dimension": i.dimension,
                "control_item": i.control_item,
                "level": i.level,
                "rating": i.rating,
                "rating_label": RATING_LABELS.get(i.rating, i.rating),
                "score": i.score,
                "evidence": i.evidence,
                "remarks": i.remarks
            }
            for i in items
        ]
    }


@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, task_update: AssessmentTaskUpdate, db: Session = Depends(get_db)):
    """更新任务信息"""
    db_task = db.query(AssessmentTask).filter(AssessmentTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    db_task.updated_at = datetime.now()
    db.commit()
    db.refresh(db_task)
    
    return {"message": "任务更新成功"}


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """删除评估任务"""
    db_task = db.query(AssessmentTask).filter(AssessmentTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    db.delete(db_task)
    db.commit()
    
    return {"message": "任务删除成功"}


# ============ 评估项接口 ============

@app.put("/api/tasks/{task_id}/items/{item_id}")
def update_item(task_id: int, item_id: int, item_update: AssessmentItemUpdate, db: Session = Depends(get_db)):
    """更新评估项"""
    db_item = db.query(AssessmentItem).filter(
        AssessmentItem.id == item_id,
        AssessmentItem.task_id == task_id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="评估项不存在")
    
    db_item.rating = item_update.rating
    if item_update.evidence is not None:
        db_item.evidence = item_update.evidence
    if item_update.remarks is not None:
        db_item.remarks = item_update.remarks
    
    # 计算得分
    if item_update.rating in RATING_SCORES:
        score_ratio = RATING_SCORES[item_update.rating]
        if score_ratio is not None:
            db_item.score = score_ratio * 5  # 假设满分 5 分
        else:
            db_item.score = 0  # 不适用
    
    db.commit()
    
    # 重新计算任务总分
    recalculate_task_score(db, task_id)
    
    return {"message": "评估项更新成功"}


def recalculate_task_score(db: Session, task_id: int):
    """重新计算任务总分和合规率"""
    items = db.query(AssessmentItem).filter(AssessmentItem.task_id == task_id).all()
    
    total_score = sum(i.score for i in items)
    max_score = len(items) * 5  # 每项满分 5 分
    
    # 计算合规率（排除不适用的项）
    applicable_items = [i for i in items if i.rating != "not_applicable"]
    compliant_items = [i for i in applicable_items if i.rating == "compliant"]
    
    compliance_rate = (len(compliant_items) / len(applicable_items) * 100) if applicable_items else 0
    
    db_task = db.query(AssessmentTask).filter(AssessmentTask.id == task_id).first()
    if db_task:
        db_task.total_score = total_score
        db_task.compliance_rate = round(compliance_rate, 2)
        db_task.updated_at = datetime.now()
        db.commit()


@app.get("/api/tasks/{task_id}/result")
def get_task_result(task_id: int, db: Session = Depends(get_db)):
    """获取评估结果分析"""
    task = db.query(AssessmentTask).filter(AssessmentTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    items = db.query(AssessmentItem).filter(AssessmentItem.task_id == task_id).all()
    template = db.query(StandardTemplate).filter(StandardTemplate.id == task.template_id).first()
    
    # 统计
    total_items = len(items)
    completed_items = len([i for i in items if i.rating not in ["not_started", "not_applicable"]])
    total_score = sum(i.score for i in items)
    max_score = total_items * 5
    
    # 维度得分
    dimension_scores = {}
    if template and template.dimensions:
        for dim in template.dimensions:
            dim_items = [i for i in items if i.dimension == dim["id"]]
            if dim_items:
                dim_score = sum(i.score for i in dim_items)
                dim_max = len(dim_items) * 5
                dimension_scores[dim["name"]] = round(dim_score / dim_max * 100, 2) if dim_max > 0 else 0
    
    # 等级分布
    level_distribution = {
        "compliant": len([i for i in items if i.rating == "compliant"]),
        "partial": len([i for i in items if i.rating == "partial"]),
        "non_compliant": len([i for i in items if i.rating == "non_compliant"]),
        "not_applicable": len([i for i in items if i.rating == "not_applicable"])
    }
    
    return {
        "task_id": task_id,
        "total_items": total_items,
        "completed_items": completed_items,
        "total_score": total_score,
        "max_score": max_score,
        "compliance_rate": task.compliance_rate,
        "dimension_scores": dimension_scores,
        "level_distribution": level_distribution
    }


# ============ 文件上传接口 ============

@app.post("/api/tasks/{task_id}/items/{item_id}/upload")
async def upload_evidence(task_id: int, item_id: int, file: UploadFile = File(...)):
    """上传证据文件"""
    # 验证任务存在
    db = SessionLocal()
    try:
        task = db.query(AssessmentTask).filter(AssessmentTask.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 保存文件
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'uploads', str(task_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 更新评估项
        db_item = db.query(AssessmentItem).filter(
            AssessmentItem.id == item_id,
            AssessmentItem.task_id == task_id
        ).first()
        if db_item:
            db_item.has_attachment = True
            db_item.evidence = (db_item.evidence or "") + f"\n[附件：{file.filename}]"
            db.commit()
        
        return {"message": "文件上传成功", "filename": file.filename}
    finally:
        db.close()


# ============ 系统接口 ============

@app.get("/api/health")
def health_check():
    """健康检查"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """获取系统统计"""
    total_tasks = db.query(func.count(AssessmentTask.id)).scalar()
    completed_tasks = db.query(func.count(AssessmentTask.id)).filter(
        AssessmentTask.status == "completed"
    ).scalar()
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": total_tasks - completed_tasks
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
