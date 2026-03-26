"""
标准模板定义
包含各种网络安全、数据安全标准的评估模板
"""


def get_default_templates():
    """获取默认标准模板列表"""
    return [
        get_dsmm_template(),
        get_djcp_template(),
        get_grxxb_template(),
        get_djcp_data_level1_template(),  # 等保数据安全第一级
        get_djcp_data_template(),  # 等保数据安全第三级
    ]


def get_dsmm_template():
    """DSMM 数据安全能力成熟度模型模板"""
    return {
        "id": "dsmm",
        "name": "数据安全能力成熟度模型 (DSMM)",
        "standard_no": "GB/T 37988-2019",
        "version": "2019",
        "description": "数据安全能力成熟度模型，从组织建设、制度流程、技术工具、人员能力四个维度评估数据安全能力",
        "dimensions": [
            {"id": "org", "name": "组织建设", "weight": 0.25},
            {"id": "policy", "name": "制度流程", "weight": 0.25},
            {"id": "tech", "name": "技术工具", "weight": 0.25},
            {"id": "people", "name": "人员能力", "weight": 0.25},
        ],
        "items": [
            # 组织建设维度
            {"id": "dsmm-org-01", "dimension": "org", "level": "1", "content": "是否建立了数据安全组织架构", "max_score": 5},
            {"id": "dsmm-org-02", "dimension": "org", "level": "1", "content": "是否明确数据安全责任部门和责任人", "max_score": 5},
            {"id": "dsmm-org-03", "dimension": "org", "level": "2", "content": "是否设立数据安全决策机构", "max_score": 5},
            {"id": "dsmm-org-04", "dimension": "org", "level": "2", "content": "是否建立数据安全协调机制", "max_score": 5},
            {"id": "dsmm-org-05", "dimension": "org", "level": "3", "content": "是否建立数据安全绩效考核机制", "max_score": 5},
            
            # 制度流程维度
            {"id": "dsmm-policy-01", "dimension": "policy", "level": "1", "content": "是否制定数据安全总体方针", "max_score": 5},
            {"id": "dsmm-policy-02", "dimension": "policy", "level": "1", "content": "是否制定数据安全管理制度", "max_score": 5},
            {"id": "dsmm-policy-03", "dimension": "policy", "level": "2", "content": "是否制定数据分类分级管理规范", "max_score": 5},
            {"id": "dsmm-policy-04", "dimension": "policy", "level": "2", "content": "是否建立数据安全操作规程", "max_score": 5},
            {"id": "dsmm-policy-05", "dimension": "policy", "level": "3", "content": "是否定期评审和更新安全制度", "max_score": 5},
            
            # 技术工具维度
            {"id": "dsmm-tech-01", "dimension": "tech", "level": "1", "content": "是否部署基础安全防护工具", "max_score": 5},
            {"id": "dsmm-tech-02", "dimension": "tech", "level": "2", "content": "是否实现数据加密存储", "max_score": 5},
            {"id": "dsmm-tech-03", "dimension": "tech", "level": "2", "content": "是否实现数据传输加密", "max_score": 5},
            {"id": "dsmm-tech-04", "dimension": "tech", "level": "3", "content": "是否建立数据访问控制机制", "max_score": 5},
            {"id": "dsmm-tech-05", "dimension": "tech", "level": "3", "content": "是否部署数据安全审计系统", "max_score": 5},
            {"id": "dsmm-tech-06", "dimension": "tech", "level": "4", "content": "是否实现数据安全态势感知", "max_score": 5},
            
            # 人员能力维度
            {"id": "dsmm-people-01", "dimension": "people", "level": "1", "content": "是否开展数据安全意识培训", "max_score": 5},
            {"id": "dsmm-people-02", "dimension": "people", "level": "2", "content": "是否对关键岗位人员进行专业技能培训", "max_score": 5},
            {"id": "dsmm-people-03", "dimension": "people", "level": "2", "content": "是否签订保密协议", "max_score": 5},
            {"id": "dsmm-people-04", "dimension": "people", "level": "3", "content": "是否建立人员能力评估机制", "max_score": 5},
            {"id": "dsmm-people-05", "dimension": "people", "level": "4", "content": "是否建立数据安全专业认证体系", "max_score": 5},
        ]
    }


def get_djcp_template():
    """等保 2.0 基本要求模板（简化版）"""
    return {
        "id": "djcp",
        "name": "网络安全等级保护基本要求",
        "standard_no": "GB/T 22239-2019",
        "version": "2019",
        "description": "网络安全等级保护 2.0 基本要求，适用于第二级及以上信息系统",
        "dimensions": [
            {"id": "tech", "name": "技术要求", "weight": 0.6},
            {"id": "manage", "name": "管理要求", "weight": 0.4},
        ],
        "items": [
            # 技术要求 - 安全物理环境
            {"id": "djcp-tech-01", "dimension": "tech", "level": "2", "content": "机房选址是否符合安全要求", "max_score": 5},
            {"id": "djcp-tech-02", "dimension": "tech", "level": "2", "content": "是否部署门禁系统", "max_score": 5},
            {"id": "djcp-tech-03", "dimension": "tech", "level": "2", "content": "是否配置消防设施", "max_score": 5},
            {"id": "djcp-tech-04", "dimension": "tech", "level": "2", "content": "是否配置 UPS 不间断电源", "max_score": 5},
            
            # 技术要求 - 安全通信网络
            {"id": "djcp-tech-05", "dimension": "tech", "level": "2", "content": "网络架构是否合理划分安全域", "max_score": 5},
            {"id": "djcp-tech-06", "dimension": "tech", "level": "2", "content": "是否部署防火墙", "max_score": 5},
            {"id": "djcp-tech-07", "dimension": "tech", "level": "2", "content": "通信传输是否加密", "max_score": 5},
            
            # 技术要求 - 安全区域边界
            {"id": "djcp-tech-08", "dimension": "tech", "level": "2", "content": "是否部署入侵检测系统", "max_score": 5},
            {"id": "djcp-tech-09", "dimension": "tech", "level": "2", "content": "是否部署恶意代码防护", "max_score": 5},
            
            # 技术要求 - 安全计算环境
            {"id": "djcp-tech-10", "dimension": "tech", "level": "2", "content": "是否实施身份鉴别", "max_score": 5},
            {"id": "djcp-tech-11", "dimension": "tech", "level": "2", "content": "是否实施访问控制", "max_score": 5},
            {"id": "djcp-tech-12", "dimension": "tech", "level": "2", "content": "是否部署安全审计", "max_score": 5},
            
            # 管理要求 - 安全管理制度
            {"id": "djcp-manage-01", "dimension": "manage", "level": "2", "content": "是否建立网络安全管理制度", "max_score": 5},
            {"id": "djcp-manage-02", "dimension": "manage", "level": "2", "content": "是否定期评审安全制度", "max_score": 5},
            
            # 管理要求 - 安全管理机构
            {"id": "djcp-manage-03", "dimension": "manage", "level": "2", "content": "是否设立网络安全管理部门", "max_score": 5},
            {"id": "djcp-manage-04", "dimension": "manage", "level": "2", "content": "是否配备专职安全管理人员", "max_score": 5},
            
            # 管理要求 - 安全管理人员
            {"id": "djcp-manage-05", "dimension": "manage", "level": "2", "content": "是否开展安全意识培训", "max_score": 5},
            {"id": "djcp-manage-06", "dimension": "manage", "level": "2", "content": "是否签订保密协议", "max_score": 5},
            
            # 管理要求 - 安全建设管理
            {"id": "djcp-manage-07", "dimension": "manage", "level": "2", "content": "是否进行安全方案设计", "max_score": 5},
            {"id": "djcp-manage-08", "dimension": "manage", "level": "2", "content": "是否进行产品采购管理", "max_score": 5},
            
            # 管理要求 - 安全运维管理
            {"id": "djcp-manage-09", "dimension": "manage", "level": "2", "content": "是否建立日常运维管理制度", "max_score": 5},
            {"id": "djcp-manage-10", "dimension": "manage", "level": "2", "content": "是否制定应急预案并演练", "max_score": 5},
        ]
    }


def get_grxxb_template():
    """个人信息安全规范模板"""
    return {
        "id": "grxxb",
        "name": "个人信息安全规范",
        "standard_no": "GB/T 35273-2020",
        "version": "2020",
        "description": "个人信息安全规范，适用于各类组织的个人信息处理活动",
        "dimensions": [
            {"id": "collect", "name": "收集", "weight": 0.2},
            {"id": "store", "name": "存储", "weight": 0.2},
            {"id": "use", "name": "使用", "weight": 0.2},
            {"id": "share", "name": "共享转让", "weight": 0.2},
            {"id": "delete", "name": "删除", "weight": 0.2},
        ],
        "items": [
            # 收集
            {"id": "grxxb-collect-01", "dimension": "collect", "level": "基础", "content": "是否公开收集使用规则", "max_score": 5},
            {"id": "grxxb-collect-02", "dimension": "collect", "level": "基础", "content": "是否明示收集目的、方式和范围", "max_score": 5},
            {"id": "grxxb-collect-03", "dimension": "collect", "level": "基础", "content": "是否征得用户同意", "max_score": 5},
            {"id": "grxxb-collect-04", "dimension": "collect", "level": "基础", "content": "是否遵循最小必要原则", "max_score": 5},
            
            # 存储
            {"id": "grxxb-store-01", "dimension": "store", "level": "基础", "content": "是否采取加密存储措施", "max_score": 5},
            {"id": "grxxb-store-02", "dimension": "store", "level": "基础", "content": "是否设定存储期限", "max_score": 5},
            {"id": "grxxb-store-03", "dimension": "store", "level": "基础", "content": "是否采取去标识化措施", "max_score": 5},
            
            # 使用
            {"id": "grxxb-use-01", "dimension": "use", "level": "基础", "content": "是否按约定目的使用个人信息", "max_score": 5},
            {"id": "grxxb-use-02", "dimension": "use", "level": "基础", "content": "是否限制访问权限", "max_score": 5},
            {"id": "grxxb-use-03", "dimension": "use", "level": "基础", "content": "是否进行安全影响评估", "max_score": 5},
            
            # 共享转让
            {"id": "grxxb-share-01", "dimension": "share", "level": "基础", "content": "共享前是否进行安全评估", "max_score": 5},
            {"id": "grxxb-share-02", "dimension": "share", "level": "基础", "content": "是否与接收方签订协议", "max_score": 5},
            {"id": "grxxb-share-03", "dimension": "share", "level": "基础", "content": "是否告知用户共享情况", "max_score": 5},
            
            # 删除
            {"id": "grxxb-delete-01", "dimension": "delete", "level": "基础", "content": "是否响应用户删除请求", "max_score": 5},
            {"id": "grxxb-delete-02", "dimension": "delete", "level": "基础", "content": "超期后是否及时删除", "max_score": 5},
        ]
    }


# 评分规则
RATING_SCORES = {
    "compliant": 1.0,      # 符合 - 100%
    "partial": 0.5,        # 部分符合 - 50%
    "non_compliant": 0.0,  # 不符合 - 0%
    "not_applicable": None # 不适用 - 不计分
}

RATING_LABELS = {
    "compliant": "符合",
    "partial": "部分符合",
    "non_compliant": "不符合",
    "not_applicable": "不适用"
}


def get_djcp_data_level1_template():
    """等保数据安全第一级系统评估模板（自主保护级）"""
    return {
        "id": "djcp_data_level1",
        "name": "信息安全技术 网络安全等级保护数据安全基本要求（第一级）",
        "standard_no": "GA/T 2380-2026",
        "version": "2026",
        "description": "公共安全行业标准 - 网络安全等级保护数据安全基本要求 第一级（自主保护级），适用于一般信息系统。包含 4.1-4.8 共 9 条基本要求。",
        "dimensions": [
            {"id": "data_classify", "name": "数据分类分级", "weight": 0.15},
            {"id": "data_collect", "name": "数据采集安全", "weight": 0.10},
            {"id": "data_transfer", "name": "数据传输安全", "weight": 0.15},
            {"id": "data_store", "name": "数据存储安全", "weight": 0.15},
            {"id": "data_use", "name": "数据使用安全", "weight": 0.15},
            {"id": "data_share", "name": "数据交换共享", "weight": 0.15},
            {"id": "data_delete", "name": "数据销毁安全", "weight": 0.15},
        ],
        "items": [
            # 4.1 数据分类分级
            {"id": "djcp-data-l1-4.1", "dimension": "data_classify", "level": "一级", "content": "4.1 应建立数据分类分级管理制度，明确数据分类分级方法和管理要求", "max_score": 5},
            
            # 4.2 数据采集安全
            {"id": "djcp-data-l1-4.2", "dimension": "data_collect", "level": "一级", "content": "4.2 应明确数据采集的目的、方式和范围，遵循合法、正当、必要的原则", "max_score": 5},
            
            # 4.3 数据传输安全
            {"id": "djcp-data-l1-4.3-a", "dimension": "data_transfer", "level": "一级", "content": "4.3 a) 应在重要数据传输前进行加密处理", "max_score": 5},
            {"id": "djcp-data-l1-4.3-b", "dimension": "data_transfer", "level": "一级", "content": "4.3 b) 应采用安全的传输协议进行数据传输", "max_score": 5},
            
            # 4.4 数据存储安全
            {"id": "djcp-data-l1-4.4-a", "dimension": "data_store", "level": "一级", "content": "4.4 a) 应对重要数据存储进行加密保护", "max_score": 5},
            {"id": "djcp-data-l1-4.4-b", "dimension": "data_store", "level": "一级", "content": "4.4 b) 应建立数据备份机制，定期备份重要数据", "max_score": 5},
            
            # 4.5 数据使用安全
            {"id": "djcp-data-l1-4.5", "dimension": "data_use", "level": "一级", "content": "4.5 应建立数据访问控制机制，根据业务需要分配数据访问权限", "max_score": 5},
            
            # 4.6 数据交换共享安全
            {"id": "djcp-data-l1-4.6", "dimension": "data_share", "level": "一级", "content": "4.6 应在数据交换共享前与接收方签订安全协议，明确安全责任和保护要求", "max_score": 5},
            
            # 4.7 数据销毁安全
            {"id": "djcp-data-l1-4.7", "dimension": "data_delete", "level": "一级", "content": "4.7 应建立数据销毁管理制度，采用技术手段确保数据无法被恢复", "max_score": 5},
            
            # 4.8 安全事件处置
            {"id": "djcp-data-l1-4.8", "dimension": "data_use", "level": "一级", "content": "4.8 应建立数据安全事件应急处置机制，及时响应和处置数据安全事件", "max_score": 5},
        ]
    }


def get_djcp_data_template():
    """网络安全等级保护数据安全基本要求模板（三级系统专用）"""
    return {
        "id": "djcp_data",
        "name": "信息安全技术 网络安全等级保护数据安全基本要求（第三级）",
        "standard_no": "GA/T 2380-2026",
        "version": "2026",
        "description": "公共安全行业标准 - 网络安全等级保护数据安全基本要求 第三级（监督保护级），适用于关键信息基础设施和重要信息系统。评估选项：满足、部分满足、不满足、不适用",
        "dimensions": [
            {"id": "data_classify", "name": "数据分类分级", "weight": 0.15},
            {"id": "data_collect", "name": "数据采集安全", "weight": 0.15},
            {"id": "data_transfer", "name": "数据传输安全", "weight": 0.15},
            {"id": "data_store", "name": "数据存储安全", "weight": 0.15},
            {"id": "data_use", "name": "数据使用安全", "weight": 0.15},
            {"id": "data_share", "name": "数据交换共享", "weight": 0.15},
            {"id": "data_delete", "name": "数据销毁安全", "weight": 0.10},
        ],
        "items": [
            # ==================== 数据分类分级 ====================
            {"id": "djcp-data-class-01", "dimension": "data_classify", "level": "二级", "content": "是否建立数据分类分级管理制度", "max_score": 5},
            {"id": "djcp-data-class-02", "dimension": "data_classify", "level": "二级", "content": "是否识别重要数据和核心数据", "max_score": 5},
            {"id": "djcp-data-class-03", "dimension": "data_classify", "level": "二级", "content": "是否制定数据分类分级指南", "max_score": 5},
            {"id": "djcp-data-class-04", "dimension": "data_classify", "level": "三级", "content": "是否建立数据分类分级动态调整机制", "max_score": 5},
            {"id": "djcp-data-class-05", "dimension": "data_classify", "level": "三级", "content": "是否对不同级别数据实施差异化保护", "max_score": 5},
            
            # ==================== 数据采集安全 ====================
            {"id": "djcp-data-coll-01", "dimension": "data_collect", "level": "二级", "content": "是否明确数据采集目的和范围", "max_score": 5},
            {"id": "djcp-data-coll-02", "dimension": "data_collect", "level": "二级", "content": "是否遵循最小必要原则采集数据", "max_score": 5},
            {"id": "djcp-data-coll-03", "dimension": "data_collect", "level": "二级", "content": "是否验证数据来源的合法性和真实性", "max_score": 5},
            {"id": "djcp-data-coll-04", "dimension": "data_collect", "level": "三级", "content": "是否对采集的个人信息征得用户同意", "max_score": 5},
            {"id": "djcp-data-coll-05", "dimension": "data_collect", "level": "三级", "content": "是否建立采集数据质量校验机制", "max_score": 5},
            {"id": "djcp-data-coll-06", "dimension": "data_collect", "level": "三级", "content": "是否对批量采集行为进行安全评估", "max_score": 5},
            
            # ==================== 数据传输安全 ====================
            {"id": "djcp-data-trans-01", "dimension": "data_transfer", "level": "二级", "content": "是否对敏感数据传输进行加密", "max_score": 5},
            {"id": "djcp-data-trans-02", "dimension": "data_transfer", "level": "二级", "content": "是否采用安全的传输协议 (如 HTTPS/TLS)", "max_score": 5},
            {"id": "djcp-data-trans-03", "dimension": "data_transfer", "level": "二级", "content": "是否验证通信双方身份", "max_score": 5},
            {"id": "djcp-data-trans-04", "dimension": "data_transfer", "level": "三级", "content": "是否对重要数据实施端到端加密", "max_score": 5},
            {"id": "djcp-data-trans-05", "dimension": "data_transfer", "level": "三级", "content": "是否建立数据传输完整性校验机制", "max_score": 5},
            {"id": "djcp-data-trans-06", "dimension": "data_transfer", "level": "三级", "content": "是否对跨境数据传输进行安全评估", "max_score": 5},
            
            # ==================== 数据存储安全 ====================
            {"id": "djcp-data-store-01", "dimension": "data_store", "level": "二级", "content": "是否对存储的敏感数据进行加密", "max_score": 5},
            {"id": "djcp-data-store-02", "dimension": "data_store", "level": "二级", "content": "是否建立数据备份机制", "max_score": 5},
            {"id": "djcp-data-store-03", "dimension": "data_store", "level": "二级", "content": "是否定期测试数据恢复能力", "max_score": 5},
            {"id": "djcp-data-store-04", "dimension": "data_store", "level": "三级", "content": "是否对重要数据实施异地备份", "max_score": 5},
            {"id": "djcp-data-store-05", "dimension": "data_store", "level": "三级", "content": "是否建立存储介质安全管理制度", "max_score": 5},
            {"id": "djcp-data-store-06", "dimension": "data_store", "level": "三级", "content": "是否对数据库实施访问控制和审计", "max_score": 5},
            {"id": "djcp-data-store-07", "dimension": "data_store", "level": "三级", "content": "是否设定数据存储期限并定期清理", "max_score": 5},
            
            # ==================== 数据使用安全 ====================
            {"id": "djcp-data-use-01", "dimension": "data_use", "level": "二级", "content": "是否建立数据访问权限管理制度", "max_score": 5},
            {"id": "djcp-data-use-02", "dimension": "data_use", "level": "二级", "content": "是否实施数据访问权限审批", "max_score": 5},
            {"id": "djcp-data-use-03", "dimension": "data_use", "level": "二级", "content": "是否遵循权限最小化原则", "max_score": 5},
            {"id": "djcp-data-use-04", "dimension": "data_use", "level": "三级", "content": "是否对重要数据操作进行审计记录", "max_score": 5},
            {"id": "djcp-data-use-05", "dimension": "data_use", "level": "三级", "content": "是否对敏感数据展示进行脱敏处理", "max_score": 5},
            {"id": "djcp-data-use-06", "dimension": "data_use", "level": "三级", "content": "是否建立数据使用安全监控机制", "max_score": 5},
            {"id": "djcp-data-use-07", "dimension": "data_use", "level": "三级", "content": "是否对批量导出行为进行审批和审计", "max_score": 5},
            {"id": "djcp-data-use-08", "dimension": "data_use", "level": "三级", "content": "是否建立数据使用安全事件应急响应机制", "max_score": 5},
            
            # ==================== 数据交换共享 ====================
            {"id": "djcp-data-share-01", "dimension": "data_share", "level": "二级", "content": "是否建立数据共享安全管理制度", "max_score": 5},
            {"id": "djcp-data-share-02", "dimension": "data_share", "level": "二级", "content": "是否与数据接收方签订安全协议", "max_score": 5},
            {"id": "djcp-data-share-03", "dimension": "data_share", "level": "二级", "content": "是否验证数据接收方的安全保护能力", "max_score": 5},
            {"id": "djcp-data-share-04", "dimension": "data_share", "level": "三级", "content": "是否对数据共享进行安全影响评估", "max_score": 5},
            {"id": "djcp-data-share-05", "dimension": "data_share", "level": "三级", "content": "是否对共享数据进行分类分级标识", "max_score": 5},
            {"id": "djcp-data-share-06", "dimension": "data_share", "level": "三级", "content": "是否建立数据共享审计和追溯机制", "max_score": 5},
            {"id": "djcp-data-share-07", "dimension": "data_share", "level": "三级", "content": "是否对数据转让行为进行审批", "max_score": 5},
            
            # ==================== 数据销毁安全 ====================
            {"id": "djcp-data-del-01", "dimension": "data_delete", "level": "二级", "content": "是否建立数据销毁管理制度", "max_score": 5},
            {"id": "djcp-data-del-02", "dimension": "data_delete", "level": "二级", "content": "是否对存储介质进行安全销毁", "max_score": 5},
            {"id": "djcp-data-del-03", "dimension": "data_delete", "level": "二级", "content": "是否记录数据销毁过程", "max_score": 5},
            {"id": "djcp-data-del-04", "dimension": "data_delete", "level": "三级", "content": "是否采用不可恢复的销毁方式", "max_score": 5},
            {"id": "djcp-data-del-05", "dimension": "data_delete", "level": "三级", "content": "是否对数据销毁进行监督和验证", "max_score": 5},
            {"id": "djcp-data-del-06", "dimension": "data_delete", "level": "三级", "content": "是否对委托销毁进行安全管控", "max_score": 5},
        ]
    }
