from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import get_db, User, Template, Clause, AssessmentTask, AssessmentResultItem, AssessmentResult, init_db
from ..services.llm_service import LLMService
import os
import json
import hashlib
import secrets
import string
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def generate_strong_password(length=16) -> str:
    """生成强密码"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

# Pydantic 模型
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str

class TaskCreate(BaseModel):
    task_name: str
    organization: str
    system_name: str
    template_id: int
    business_status: str

class ExcelTaskCreate(BaseModel):
    task_name: str
    organization: str
    system_name: str

# 初始化数据库并创建预设账号
def init_app():
    init_db()
    db = next(get_db())
    try:
        # 创建预设账号
        preset_users = [
            ("test1", generate_strong_password()),
            ("test2", generate_strong_password()),
            ("test3", generate_strong_password()),
            ("test4", generate_strong_password()),
            ("test5", generate_strong_password()),
        ]
        
        print("\n=== 预设账号密码 ===")
        for username, password in preset_users:
            if not db.query(User).filter(User.username == username).first():
                hashed = hash_password(password)
                db_user = User(username=username, password_hash=hashed)
                db.add(db_user)
                print(f"{username}: {password}")
        db.commit()
        print("===================\n")
    finally:
        db.close()

init_app()

def get_llm_service():
    api_key = os.getenv("DASHSCOPE_API_KEY", "")
    return LLMService(api_key=api_key if api_key else None)


# ============ 用户认证 ============

@router.post("/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return {"id": db_user.id, "username": db_user.username}


@router.get("/auth/accounts")
def list_accounts(db: Session = Depends(get_db)):
    """获取账号列表（管理员）"""
    users = db.query(User).all()
    return [{
        "id": u.id,
        "username": u.username,
        "created_at": u.created_at.isoformat() if u.created_at else None
    } for u in users]


@router.post("/auth/accounts")
def create_account(user: UserCreate, db: Session = Depends(get_db)):
    """创建新账号（管理员）"""
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    hashed = hash_password(user.password)
    db_user = User(username=user.username, password_hash=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username}


# ============ 评估模版 ============

@router.post("/templates/upload")
def upload_template(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    level: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service)
):
    """上传标准文件并智能拆解条款，或上传 Excel 导入人工拆解的条款"""
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
    
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    db_template = Template(name=name, description=description, level=level, file_path=file_path)
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    clauses = []
    
    # 判断是否为 Excel 文件（人工拆解的条款）
    if file.filename.lower().endswith(('.xlsx', '.xls')):
        try:
            import pandas as pd
            df = pd.read_excel(file_path)
            
            # 支持的列名映射
            seq_col = None
            pa_col = None
            pa_name_col = None
            std_no_col = None
            content_col = None
            
            # 自动识别列名
            for col in df.columns:
                col_lower = str(col).lower().strip()
                if col_lower in ['序号', 'seq', 'no']:
                    seq_col = col
                elif col_lower in ['pa 编号', 'pa', 'pa 号']:
                    pa_col = col
                elif col_lower in ['pa 名称', 'pa 名字', '能力域']:
                    pa_name_col = col
                elif col_lower in ['标准编号', '条款编号', '编号']:
                    std_no_col = col
                elif col_lower in ['条款内容', '内容', '条款']:
                    content_col = col
            
            if not content_col:
                # 尝试使用第一列作为内容
                content_col = df.columns[0] if len(df.columns) > 0 else None
            
            if content_col:
                for idx, row in df.iterrows():
                    clause = Clause(
                        template_id=db_template.id,
                        clause_number=str(row.get(std_no_col, f"clause-{idx+1}")) if std_no_col else f"clause-{idx+1}",
                        clause_content=str(row.get(content_col, '')),
                        requirement=str(row.get(pa_name_col, row.get(pa_col, ''))) if pa_name_col or pa_col else '',
                        domain=str(row.get(pa_name_col, '')) if pa_name_col else '',
                        sub_domain=str(row.get(pa_col, '')) if pa_col else '',
                        seq=int(row.get(seq_col, idx+1)) if seq_col else idx+1
                    )
                    db.add(clause)
                    clauses.append(clause)
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Excel 解析失败：{str(e)}")
    else:
        # PDF/Word 文件，使用大模型智能拆解
        content = ""
        try:
            from ..utils.pdf_parser import extract_text_from_file
            content = extract_text_from_file(file_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"文件解析失败：{e}")
        
        if not content or len(content.strip()) < 100:
            raise HTTPException(status_code=400, detail="文件内容过少或无法提取文本，请检查文件是否有效")
        
        # 根据标准类型选择拆解方法
        if 'DSMM' in name.upper() or '数据安全能力成熟度' in name:
            clauses = llm.extract_dsmm_clauses(content, level or "三级")
        else:
            clauses = llm.extract_clauses(content, name)
        
        for clause_data in clauses:
            clause = Clause(
                template_id=db_template.id,
                clause_number=clause_data.get('clause_number', ''),
                clause_content=clause_data.get('clause_content', ''),
                requirement=clause_data.get('requirement', ''),
                domain=clause_data.get('domain', ''),
                sub_domain=clause_data.get('sub_domain', ''),
                seq=clause_data.get('seq', 0)
            )
            db.add(clause)
        
        db.commit()
    
    return {
        "template_id": db_template.id,
        "name": db_template.name,
        "clauses_count": len(clauses)
    }


@router.get("/templates")
def list_templates(db: Session = Depends(get_db)):
    """获取模版列表"""
    templates = db.query(Template).all()
    return [{
        "id": t.id,
        "name": t.name,
        "description": t.description,
        "level": t.level,
        "clauses_count": len(t.clauses),
        "created_at": t.created_at.isoformat() if t.created_at else None
    } for t in templates]


@router.get("/templates/{template_id}")
def get_template(template_id: int, db: Session = Depends(get_db)):
    """获取模版详情"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模版不存在")
    
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "level": template.level,
        "clauses": [{
            "id": c.id,
            "clause_number": c.clause_number,
            "clause_content": c.clause_content,
            "requirement": c.requirement,
            "domain": c.domain,
            "sub_domain": c.sub_domain,
            "seq": c.seq
        } for c in template.clauses]
    }


@router.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """删除模版及关联条款"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模版不存在")
    
    # 删除关联的条款
    db.query(Clause).filter(Clause.template_id == template_id).delete()
    
    # 删除模版
    db.delete(template)
    db.commit()
    
    return {"status": "ok", "message": f"模版 {template.name} 已删除"}


# ============ 评估任务 ============

@router.post("/tasks")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """创建评估任务"""
    template = db.query(Template).filter(Template.id == task.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模版不存在")
    
    db_task = AssessmentTask(
        task_name=task.task_name,
        organization=task.organization,
        system_name=task.system_name,
        template_id=task.template_id,
        business_status=task.business_status,
        status="pending"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return {"task_id": db_task.id, "status": "pending"}


@router.post("/tasks/excel")
def create_task_from_excel(
    task_name: str = Form(...),
    organization: str = Form(...),
    system_name: str = Form(...),
    template_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """从 Excel 导入创建评估任务（Excel 包含条款和业务现状）"""
    import pandas as pd
    
    # 验证模版是否存在
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模版不存在")
    
    # 保存上传的 Excel 文件
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
    
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    # 创建任务
    db_task = AssessmentTask(
        task_name=task_name,
        organization=organization,
        system_name=system_name,
        template_id=template_id,
        business_status="",  # Excel 导入时，业务现状在条款级别
        status="pending"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # 解析 Excel 文件
    try:
        df = pd.read_excel(file_path)
        
        # 支持的列名映射
        clause_no_col = None
        clause_content_col = None
        requirement_col = None
        business_status_col = None
        domain_col = None
        sub_domain_col = None
        seq_col = None
        
        # 自动识别列名
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if col_lower in ['条款编号', '标准编号', '编号', 'clause_no', 'clause_number']:
                clause_no_col = col
            elif col_lower in ['条款内容', '内容', '条款', 'clause_content', 'content']:
                clause_content_col = col
            elif col_lower in ['评估要求', '要求', 'requirement', 'req']:
                requirement_col = col
            elif col_lower in ['评估现状', '业务现状', '现状', 'business_status', 'status', 'evidence', 'current_status']:
                business_status_col = col
            elif col_lower in ['能力域', 'domain', 'pa 名称']:
                domain_col = col
            elif col_lower in ['pa', '子域', 'sub_domain', 'sub domain']:
                sub_domain_col = col
            elif col_lower in ['序号', 'seq', 'no', 'index']:
                seq_col = col
        
        if not clause_content_col:
            # 尝试使用第一列作为内容
            clause_content_col = df.columns[0] if len(df.columns) > 0 else None
        
        if not clause_content_col:
            raise HTTPException(status_code=400, detail="Excel 中未找到条款内容列，请确保包含'条款内容'或'内容'列")
        
        # 导入条款和业务现状
        imported_count = 0
        for idx, row in df.iterrows():
            clause_number = str(row.get(clause_no_col, f"clause-{idx+1}")) if clause_no_col else f"clause-{idx+1}"
            clause_content = str(row.get(clause_content_col, ''))
            requirement = str(row.get(requirement_col, '')) if requirement_col else ''
            business_status = str(row.get(business_status_col, '')) if business_status_col else ''
            domain = str(row.get(domain_col, '')) if domain_col else ''
            sub_domain = str(row.get(sub_domain_col, '')) if sub_domain_col else ''
            seq = int(row.get(seq_col, idx+1)) if seq_col else idx+1
            
            # 跳过空行
            if not clause_content or not clause_content.strip():
                continue
            
            # 查找或创建条款
            clause = db.query(Clause).filter(
                Clause.template_id == template_id,
                Clause.clause_number == clause_number
            ).first()
            
            if not clause:
                clause = Clause(
                    template_id=template_id,
                    clause_number=clause_number,
                    clause_content=clause_content,
                    requirement=requirement,
                    domain=domain,
                    sub_domain=sub_domain,
                    seq=seq
                )
                db.add(clause)
                db.commit()
                db.refresh(clause)
            
            # 创建评估结果项（包含业务现状）
            result_item = AssessmentResultItem(
                task_id=db_task.id,
                clause_id=clause.id,
                evidence=business_status,
                result=None,
                score=None,
                comment=None
            )
            db.add(result_item)
            imported_count += 1
        
        db.commit()
        
        # 清理上传的文件
        try:
            os.remove(file_path)
        except:
            pass
        
        return {
            "task_id": db_task.id,
            "status": "pending",
            "imported_count": imported_count,
            "message": f"成功导入 {imported_count} 条条款及业务现状"
        }
        
    except Exception as e:
        db.rollback()
        # 清理上传的文件
        try:
            os.remove(file_path)
        except:
            pass
        raise HTTPException(status_code=400, detail=f"Excel 解析失败：{str(e)}")


@router.post("/tasks/{task_id}/assess")
def assess_task(task_id: int, db: Session = Depends(get_db), llm: LLMService = Depends(get_llm_service)):
    """执行智能评估"""
    task = db.query(AssessmentTask).filter(AssessmentTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.status == "completed":
        raise HTTPException(status_code=400, detail="任务已完成评估")
    
    task.status = "processing"
    db.commit()
    
    clauses = db.query(Clause).filter(Clause.template_id == task.template_id).all()
    
    total_score = 0
    valid_count = 0
    result_items = []
    assessed_count = 0
    
    for clause in clauses:
        # 查找该条款已填写的业务现状
        existing_result = db.query(AssessmentResultItem).filter(
            AssessmentResultItem.task_id == task_id,
            AssessmentResultItem.clause_id == clause.id
        ).first()
        
        # 优先使用条款级别的业务现状，如果没有则使用任务级别的
        clause_business_status = existing_result.evidence if existing_result and existing_result.evidence else task.business_status
        
        assessment = llm.assess_clause(
            clause.clause_content,
            clause.requirement or clause.clause_content,
            clause_business_status or "无具体业务现状描述，请根据通用安全实践进行评估"
        )
        
        if existing_result:
            # 更新已有记录
            existing_result.result = AssessmentResult(assessment.get('result', '不符合'))
            existing_result.score = assessment.get('score', 0)
            existing_result.comment = assessment.get('comment', '')
            # 保留原有的 evidence（业务现状）
        else:
            # 创建新记录
            result_item = AssessmentResultItem(
                task_id=task_id,
                clause_id=clause.id,
                result=AssessmentResult(assessment.get('result', '不符合')),
                score=assessment.get('score', 0),
                evidence=clause_business_status or "",
                comment=assessment.get('comment', '')
            )
            db.add(result_item)
        
        result_items.append(assessment)
        assessed_count += 1
        
        if assessment.get('result') != '不适用':
            total_score += assessment.get('score', 0)
            valid_count += 1
    
    db.commit()
    
    final_score = (total_score / valid_count * 100) if valid_count > 0 else 0
    
    if final_score >= 85:
        level = "优秀"
    elif final_score >= 75:
        level = "良好"
    elif final_score >= 60:
        level = "合格"
    else:
        level = "不合格"
    
    task.total_score = final_score
    task.level = level
    task.status = "completed"
    task.completed_at = datetime.utcnow()
    db.commit()
    
    return {
        "task_id": task_id,
        "total_score": final_score,
        "level": level,
        "assessed_count": assessed_count
    }


@router.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    """获取任务列表"""
    tasks = db.query(AssessmentTask).order_by(AssessmentTask.created_at.desc()).all()
    return [{
        "id": t.id,
        "task_name": t.task_name,
        "organization": t.organization,
        "system_name": t.system_name,
        "template_name": t.template.name if t.template else None,
        "total_score": t.total_score,
        "level": t.level,
        "status": t.status,
        "created_at": t.created_at.isoformat() if t.created_at else None
    } for t in tasks]


@router.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    """获取任务详情"""
    task = db.query(AssessmentTask).filter(AssessmentTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 获取所有条款
    clauses = db.query(Clause).filter(Clause.template_id == task.template_id).all()
    
    # 获取已有的评估结果
    existing_results = {r.clause_id: r for r in db.query(AssessmentResultItem).filter(AssessmentResultItem.task_id == task_id).all()}
    
    # 合并条款和评估结果
    results_data = []
    for clause in clauses:
        existing = existing_results.get(clause.id)
        results_data.append({
            "id": existing.id if existing else None,
            "clause_id": clause.id,
            "clause_number": clause.clause_number,
            "clause_content": clause.clause_content,
            "domain": clause.domain,
            "sub_domain": clause.sub_domain,
            "seq": clause.seq,
            "business_status": existing.evidence if existing else "",
            "result": existing.result.value if existing and existing.result else None,
            "score": existing.score if existing else None,
            "comment": existing.comment if existing else None
        })
    
    return {
        "id": task.id,
        "task_name": task.task_name,
        "organization": task.organization,
        "system_name": task.system_name,
        "template_name": task.template.name if task.template else None,
        "business_status": task.business_status,
        "total_score": task.total_score,
        "level": task.level,
        "status": task.status,
        "results": results_data
    }


@router.put("/tasks/{task_id}/clause-status")
def update_clause_status(task_id: int, clause_id: int, business_status: str, db: Session = Depends(get_db)):
    """更新单条条款的业务现状"""
    task = db.query(AssessmentTask).filter(AssessmentTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    result_item = db.query(AssessmentResultItem).filter(
        AssessmentResultItem.task_id == task_id,
        AssessmentResultItem.clause_id == clause_id
    ).first()
    
    if result_item:
        result_item.evidence = business_status
    else:
        result_item = AssessmentResultItem(
            task_id=task_id,
            clause_id=clause_id,
            evidence=business_status
        )
        db.add(result_item)
    
    db.commit()
    return {"status": "ok"}


@router.post("/tasks/{task_id}/save-all-status")
def save_all_clause_status(task_id: int, items: list, db: Session = Depends(get_db)):
    """批量保存所有条款的业务现状"""
    task = db.query(AssessmentTask).filter(AssessmentTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    for item in items:
        clause_id = item.get("clause_id")
        business_status = item.get("business_status", "")
        
        result_item = db.query(AssessmentResultItem).filter(
            AssessmentResultItem.task_id == task_id,
            AssessmentResultItem.clause_id == clause_id
        ).first()
        
        if result_item:
            result_item.evidence = business_status
        else:
            result_item = AssessmentResultItem(
                task_id=task_id,
                clause_id=clause_id,
                evidence=business_status
            )
            db.add(result_item)
    
    db.commit()
    return {"status": "ok", "saved_count": len(items)}


# ============ 统计分析 ============

@router.get("/stats/overview")
def get_overview(db: Session = Depends(get_db)):
    """获取总体评估统计"""
    total_tasks = db.query(AssessmentTask).count()
    completed_tasks = db.query(AssessmentTask).filter(AssessmentTask.status == "completed").count()
    
    excellent = db.query(AssessmentTask).filter(AssessmentTask.level == "优秀").count()
    good = db.query(AssessmentTask).filter(AssessmentTask.level == "良好").count()
    pass_ = db.query(AssessmentTask).filter(AssessmentTask.level == "合格").count()
    failed = db.query(AssessmentTask).filter(AssessmentTask.level == "不合格").count()
    
    completed = db.query(AssessmentTask).filter(AssessmentTask.status == "completed").all()
    avg_score = sum(t.total_score or 0 for t in completed) / len(completed) if completed else 0
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "level_distribution": {
            "优秀": excellent,
            "良好": good,
            "合格": pass_,
            "不合格": failed
        },
        "average_score": round(avg_score, 1)
    }


@router.get("/tasks/{task_id}/report")
def generate_report(task_id: int, db: Session = Depends(get_db), llm: LLMService = Depends(get_llm_service)):
    """生成评估报告"""
    task = db.query(AssessmentTask).filter(AssessmentTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    results = db.query(AssessmentResultItem).filter(AssessmentResultItem.task_id == task_id).all()
    result_data = [{
        'result': r.result.value if r.result else None,
        'score': r.score,
        'evidence': r.evidence,
        'comment': r.comment
    } for r in results]
    
    summary = llm.generate_report_summary(
        task.task_name,
        task.total_score or 0,
        task.level or "未评估",
        result_data
    )
    
    report = f"""# 标准智能评估报告

## 基本信息
- 任务名称：{task.task_name}
- 评估组织：{task.organization}
- 评估系统：{task.system_name}
- 评估模版：{task.template.name if task.template else 'N/A'}
- 评估时间：{task.completed_at.strftime('%Y-%m-%d %H:%M') if task.completed_at else 'N/A'}

## 评估结论
- **评估得分**：{task.total_score:.1f}分
- **评估等级**：{task.level}

## 评估摘要
{summary}

## 详细评估结果
| 条款编号 | 条款内容 | 评估结果 | 得分 |
|---------|---------|---------|------|
"""
    
    for r in results:
        report += f"| {r.clause.clause_number} | {r.clause.clause_content[:30]}... | {r.result.value if r.result else 'N/A'} | {r.score} |\n"
    
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, f"report_{task_id}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    return {
        "task_id": task_id,
        "report_path": report_path,
        "summary": summary
    }
