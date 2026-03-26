import requests
import json
import re
import os
from typing import List, Dict


class LLMService:
    """大模型服务 - 条款拆解和智能评估 (复用 OpenClaw 配置)"""
    
    def __init__(self, api_key: str = None):
        # 优先使用 OpenClaw 配置的 API Key
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY") or "sk-sp-99b90418112340618177c5475a6ef64e"
        # 使用 OpenClaw 的 Base URL
        self.api_url = "https://coding.dashscope.aliyuncs.com/v1/chat/completions"
    
    def _call_llm(self, prompt: str, model: str = "qwen3.5-plus", max_tokens: int = 4096) -> str:
        """调用 DashScope Qwen 模型 (OpenAI 兼容接口)"""
        if not self.api_key:
            return ""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=180)
            if response.status_code == 200:
                result = response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                print(f"API 调用失败：{response.status_code} - {response.text}")
        except Exception as e:
            print(f"LLM 调用异常：{e}")
        
        return ""
    
    def extract_dsmm_clauses(self, file_content: str, level: str = "三级") -> List[Dict]:
        """
        专门针对 DSMM 标准的条款拆解
        
        DSMM 标准结构：
        - 第 6-12 章：安全能力维度（组织、人员、技术、流程等）
        - 每个能力域分 5 个等级：
          - 等级 1：初始级
          - 等级 2：可重复级
          - 等级 3：充分定义级 ← 目标
          - 等级 4：量化控制级
          - 等级 5：持续改进级
        
        返回：[{clause_number, clause_content, requirement, domain, sub_domain}, ...]
        """
        prompt = f"""你是 DSMM(数据安全能力成熟度模型)评估专家。请从以下标准内容中提取**DSMM {level}**的所有评估条款。

**提取规则：**
1. 只提取第 6 章到第 12 章中"**等级 3：充分定义**"的条款
2. 按能力域→子能力域→评估项的层级结构整理
3. 每个评估项包含：条款编号、条款内容、具体要求、所属能力域

**DSMM 能力域结构参考：**
- 安全战略与规划
- 数据安全组织
- 人员安全意识与培训
- 数据生命周期安全
- 安全技术防护
- 安全流程管理
- 合规与审计

**输出格式要求：**
输出 JSON 数组，每个评估项格式：
{{
  "clause_number": "6.1.3-01",
  "domain": "安全战略与规划",
  "sub_domain": "数据安全战略",
  "clause_content": "应制定数据安全战略文档",
  "requirement": "明确数据安全目标、范围、责任分工"
}}

**标准内容：**
{file_content[:10000]}

请仔细分析，确保提取所有**等级 3：充分定义**的评估项。DSMM {level}通常包含约 263 个评估项。

只输出 JSON 数组，不要其他内容。"""
        
        content = self._call_llm(prompt, max_tokens=8192)
        if content:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                try:
                    clauses = json.loads(json_match.group())
                    print(f"成功拆解 {len(clauses)} 个条款")
                    return clauses
                except Exception as e:
                    print(f"JSON 解析失败：{e}")
        
        return []
    
    def extract_clauses(self, file_content: str, standard_name: str) -> List[Dict]:
        """
        通用标准条款拆解
        """
        # 判断是否为 DSMM 标准
        if 'DSMM' in standard_name.upper() or '数据安全能力成熟度' in standard_name:
            level_match = re.search(r'([一二三四五])(级)', standard_name)
            level = f"{level_match.group(1)}{level_match.group(2)}" if level_match else "三级"
            return self.extract_dsmm_clauses(file_content, level)
        
        # 通用拆解
        prompt = f"""你是标准评估专家。请分析以下{standard_name}标准内容，将其拆解为独立的评估条款。

要求：
1. 每个条款包含：条款编号、条款内容、具体要求
2. 按标准的层级结构整理
3. 输出为 JSON 数组格式

标准内容：
{file_content[:8000]}

请输出 JSON 格式，示例：
[
  {{"clause_number": "1.1", "clause_content": "应建立安全管理制度", "requirement": "制定并发布安全管理制度文档"}},
  {{"clause_number": "1.2", "clause_content": "应定期进行安全培训", "requirement": "每季度至少一次全员安全培训"}}
]

只输出 JSON 数组，不要其他内容。"""
        
        content = self._call_llm(prompt)
        if content:
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
        
        return []
    
    def assess_clause(self, clause_content: str, requirement: str, business_status: str) -> Dict:
        """
        对单个条款进行智能评估
        返回：{result, score, evidence, comment}
        """
        prompt = f"""你是标准评估专家。请根据以下信息评估该条款的符合情况：

【标准条款】{clause_content}
【具体要求】{requirement}
【业务现状】{business_status[:2000]}

评估等级：
- 符合：完全满足要求 (得分 1 分)
- 部分符合：基本满足但有不足 (得分 0.6 分)
- 不符合：未满足要求 (得分 0 分)
- 不适用：该条款不适用于当前系统 (不计分)

请输出 JSON 格式：
{{
  "result": "符合/部分符合/不符合/不适用",
  "score": 1.0/0.6/0,
  "evidence": "评估依据",
  "comment": "简要评语"
}}

只输出 JSON 对象，不要其他内容。"""
        
        content = self._call_llm(prompt)
        if content:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
        
        return {
            "result": "不符合",
            "score": 0,
            "evidence": "评估失败",
            "comment": "大模型评估异常，需人工复核"
        }
    
    def generate_report_summary(self, task_name: str, total_score: float, level: str, 
                                 result_items: List[Dict]) -> str:
        """生成评估报告摘要"""
        compliant = sum(1 for r in result_items if r.get('result') == '符合')
        partial = sum(1 for r in result_items if r.get('result') == '部分符合')
        non_compliant = sum(1 for r in result_items if r.get('result') == '不符合')
        
        prompt = f"""请为以下评估任务生成一份专业报告摘要：

任务名称：{task_name}
评估得分：{total_score:.1f}分
评估等级：{level}

评估统计：
- 符合：{compliant}项
- 部分符合：{partial}项
- 不符合：{non_compliant}项

要求：
1. 总结整体评估情况
2. 指出主要优点
3. 列出关键改进建议

输出 200-300 字的报告摘要。"""
        
        content = self._call_llm(prompt)
        return content if content else f"评估得分：{total_score:.1f}分，等级：{level}"
