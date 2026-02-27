#!/usr/bin/env python3
"""
创建等保三级数据安全评估任务

使用方法:
    python3 create_level3_task.py <任务名称> <组织名称>
    
示例:
    python3 create_level3_task.py "XX 系统等保三级评估" "XX 公司"
"""

import requests
import sys
import json

API_BASE = "http://localhost:8001/api"


def create_level3_assessment(task_name: str, organization: str):
    """创建等保三级数据安全评估任务"""
    
    # 创建评估任务
    task_data = {
        "name": task_name,
        "template_id": "djcp_data",
        "organization": organization
    }
    
    print(f"📋 创建评估任务：{task_name}")
    print(f"🏢 被评估组织：{organization}")
    print(f"📊 评估标准：等保数据安全基本要求（第三级）")
    print()
    
    try:
        # 创建任务
        response = requests.post(f"{API_BASE}/tasks", json=task_data)
        if response.status_code != 200:
            print(f"❌ 创建任务失败：{response.text}")
            return None
        
        task_id = response.json()["id"]
        print(f"✅ 任务创建成功！任务 ID: {task_id}")
        print()
        
        # 获取任务详情
        response = requests.get(f"{API_BASE}/tasks/{task_id}")
        task = response.json()
        
        # 显示任务信息
        print("=" * 60)
        print("评估任务信息")
        print("=" * 60)
        print(f"任务名称：{task['name']}")
        print(f"评估标准：{task['template_name']}")
        print(f"评估项数：{len(task['items'])} 项")
        print(f"合规要求：≥90%")
        print()
        
        # 显示维度分布
        print("评估维度分布:")
        print("-" * 60)
        dimensions = {}
        for item in task['items']:
            dim = item['dimension']
            if dim not in dimensions:
                dimensions[dim] = 0
            dimensions[dim] += 1
        
        dim_names = {
            'data_classify': '数据分类分级',
            'data_collect': '数据采集安全',
            'data_transfer': '数据传输安全',
            'data_store': '数据存储安全',
            'data_use': '数据使用安全',
            'data_share': '数据交换共享',
            'data_delete': '数据销毁安全'
        }
        
        for dim_id, count in dimensions.items():
            dim_name = dim_names.get(dim_id, dim_id)
            print(f"  • {dim_name}: {count} 项")
        
        print()
        print("=" * 60)
        print("下一步操作:")
        print("=" * 60)
        print(f"1. 访问前端：http://localhost:8080")
        print(f"2. 点击「继续评估」打开任务")
        print(f"3. 逐项评估并记录证据")
        print(f"4. 目标合规率：≥90%")
        print()
        print("📖 评估指南：docs/等保三级数据安全评估专项指南.md")
        print()
        
        return task_id
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保服务已启动")
        print("   启动命令：cd standards-assessment && ./start.sh")
        return None
    except Exception as e:
        print(f"❌ 发生错误：{e}")
        return None


def main():
    if len(sys.argv) < 3:
        print("使用方法：python3 create_level3_task.py <任务名称> <组织名称>")
        print()
        print("示例:")
        print('  python3 create_level3_task.py "XX 系统等保三级评估" "XX 公司"')
        print()
        print("或者直接在 Web 界面创建评估任务")
        sys.exit(1)
    
    task_name = sys.argv[1]
    organization = sys.argv[2]
    
    task_id = create_level3_assessment(task_name, organization)
    
    if task_id:
        print(f"✅ 评估任务已就绪，任务 ID: {task_id}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
