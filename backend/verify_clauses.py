#!/usr/bin/env python3.11
"""
DSMM 三级条款校验脚本
从 PDF 提取原文，与数据库对比并修正
"""

from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import re
import sqlite3
import json

def extract_pdf_text():
    """提取 PDF 文本并清理"""
    laparams = LAParams(line_margin=0.5, word_margin=0.1, boxes_flow=0.5, detect_vertical=True)
    text = extract_text('uploads/20260310195623_3、GB:T 37988-2019《信息安全技术 数据安全能力成熟度模型》.pdf', laparams=laparams)
    
    # 清理文本 - 合并被换行打断的连续文字
    text = re.sub(r'(\S)\n(\S)', r'\1\2', text)
    text = re.sub(r' +', ' ', text)
    return text

def find_chapter_positions(text):
    """查找所有章节位置"""
    positions = []
    for match in re.finditer(r'(\d+\.\d+)\s+(PA\d+)', text):
        positions.append({
            'pos': match.start(),
            'section': match.group(1),
            'pa': match.group(2)
        })
    return positions

def extract_bp_content(text, bp_ref, search_area):
    """提取 BP 条款的完整内容"""
    # BP 内容通常包含：组织建设、制度流程、技术工具、人员能力等部分
    bp_pattern = rf'({re.escape(bp_ref)}[^B]*(?=BP\.\d+\.|$))'
    match = re.search(bp_pattern, search_area, re.DOTALL)
    if match:
        content = match.group(1).strip()
        # 清理多余空白
        content = re.sub(r'\s+', ' ', content)
        return content[:800]  # 限制长度
    return None

def extract_clauses_from_pdf(text, chapter_positions):
    """从 PDF 提取所有等级 3 条款"""
    clauses = {}
    
    for i, chap in enumerate(chapter_positions):
        start = chap['pos']
        end = chapter_positions[i+1]['pos'] if i+1 < len(chapter_positions) else len(text)
        section_text = text[start:end]
        
        pa_num = chap['pa']  # 如 PA01, PA30
        section_num = chap['section']  # 如 6.1, 12.11
        
        # 等级 3 的格式是 x.x.2.3
        level3_header = f'{section_num}.2.3'
        
        # 查找该 PA 下等级 3 的所有 BP 引用
        bp_refs = re.findall(rf'{level3_header}[^B]*(BP\.{pa_num[2:]}\.\d+)', section_text, re.DOTALL)
        
        if bp_refs:
            clauses[pa_num] = {
                'section': section_num,
                'bp_refs': bp_refs,
                'bp_contents': {}
            }
            
            # 提取每个 BP 的具体内容
            for bp_ref in bp_refs:
                content = extract_bp_content(section_text, bp_ref, section_text)
                if content:
                    clauses[pa_num]['bp_contents'][bp_ref] = content
    
    return clauses

def get_standard_number(section_num, bp_num, pa_num_int):
    """生成标准编号"""
    # 根据 DSMM 标准结构，等级 3 的编号格式是 x.x.3.x
    # 例如：6.1.3.1, 12.11.3.1
    
    # 计算该 BP 在 PA 中的序号
    chapter_base = section_num.split('.')
    if len(chapter_base) >= 2:
        std_no = f"{chapter_base[0]}.{chapter_base[1]}.3.{bp_num}"
    else:
        std_no = f"{section_num}.3.{bp_num}"
    
    return std_no

def verify_and_fix_database(pdf_clauses):
    """对比 PDF 和数据库，修正不一致的条款"""
    conn = sqlite3.connect('assessment.db')
    cursor = conn.cursor()
    
    stats = {
        'total': 0,
        'matched': 0,
        'fixed_std_no': 0,
        'fixed_content': 0,
        'fixed_both': 0
    }
    
    fixes = []
    
    # 遍历 PDF 中提取的条款
    for pa_num, data in pdf_clauses.items():
        section_num = data['section']
        bp_refs = data['bp_refs']
        bp_contents = data['bp_contents']
        
        for idx, bp_ref in enumerate(bp_refs):
            stats['total'] += 1
            
            # 从 BP 引用中提取 BP 序号
            bp_num_match = re.search(r'BP\.\d+\.(\d+)', bp_ref)
            if not bp_num_match:
                continue
            bp_num = int(bp_num_match.group(1))
            
            # 计算在数据库中的 seq
            # 需要先计算前面所有 PA 的条款总数
            seq = calculate_seq(pa_num, idx, pdf_clauses)
            
            # 查询数据库中的条款
            cursor.execute('''
                SELECT seq, clause_number, clause_content 
                FROM clauses 
                WHERE template_id=1 AND sub_domain=? 
                ORDER BY seq
            ''', (pa_num,))
            db_clauses = cursor.fetchall()
            
            if idx < len(db_clauses):
                db_row = db_clauses[idx]
                db_seq, db_std_no, db_content = db_row
                
                # 生成正确的标准编号
                correct_std_no = get_standard_number(section_num, bp_num, int(pa_num[2:]))
                
                # 获取 PDF 中的条款内容
                pdf_content = bp_contents.get(bp_ref, '')
                
                # 对比并记录差异
                std_no_match = (db_std_no == correct_std_no)
                content_match = (db_content.strip() == pdf_content.strip()[:len(db_content)]) if pdf_content else False
                
                if not std_no_match or not content_match:
                    # 需要修正
                    update_data = {
                        'seq': db_seq,
                        'pa': pa_num,
                        'bp_ref': bp_ref,
                        'old_std_no': db_std_no,
                        'new_std_no': correct_std_no,
                        'old_content': db_content[:100],
                        'new_content': pdf_content[:100] if pdf_content else 'N/A'
                    }
                    
                    # 更新数据库
                    if pdf_content:
                        cursor.execute('''
                            UPDATE clauses 
                            SET clause_number=?, clause_content=?
                            WHERE seq=? AND template_id=1
                        ''', (correct_std_no, pdf_content, db_seq))
                        stats['fixed_both'] += 1
                    else:
                        cursor.execute('''
                            UPDATE clauses 
                            SET clause_number=?
                            WHERE seq=? AND template_id=1
                        ''', (correct_std_no, db_seq))
                        stats['fixed_std_no'] += 1
                    
                    fixes.append(update_data)
                else:
                    stats['matched'] += 1
    
    conn.commit()
    conn.close()
    
    return stats, fixes

def calculate_seq(pa_num, idx_in_pa, all_clauses):
    """计算条款的 seq 序号"""
    # 按 PA 顺序累加
    total = 0
    for pa in sorted(all_clauses.keys()):
        if pa == pa_num:
            return total + idx_in_pa + 1
        total += len(all_clauses[pa]['bp_refs'])
    return total

def main():
    print("=" * 60)
    print("DSMM 三级条款校验 - 开始")
    print("=" * 60)
    print()
    
    # 1. 提取 PDF 文本
    print("步骤 1/4: 提取 PDF 文本...")
    text = extract_pdf_text()
    print(f"  PDF 文本长度：{len(text)} 字符")
    
    # 2. 查找章节位置
    print("步骤 2/4: 查找章节位置...")
    chapter_positions = find_chapter_positions(text)
    print(f"  找到 {len(chapter_positions)} 个 PA 章节")
    
    # 3. 提取条款
    print("步骤 3/4: 从 PDF 提取条款...")
    pdf_clauses = extract_clauses_from_pdf(text, chapter_positions)
    
    total_bp = sum(len(data['bp_refs']) for data in pdf_clauses.values())
    print(f"  提取到 {len(pdf_clauses)} 个 PA, 共 {total_bp} 条 BP 条款")
    print()
    
    # 显示提取结果摘要
    print("提取的 PA 结构:")
    for pa_num in sorted(pdf_clauses.keys()):
        data = pdf_clauses[pa_num]
        print(f"  {pa_num} ({data['section']}): {len(data['bp_refs'])} 条")
    print()
    
    # 4. 校验并修正数据库
    print("步骤 4/4: 校验并修正数据库...")
    stats, fixes = verify_and_fix_database(pdf_clauses)
    
    print()
    print("=" * 60)
    print("校验完成 - 统计结果")
    print("=" * 60)
    print(f"  总条款数：{stats['total']}")
    print(f"  匹配一致：{stats['matched']}")
    print(f"  已修正：{stats['total'] - stats['matched']}")
    print()
    
    if fixes:
        print("修正示例 (前 10 条):")
        for fix in fixes[:10]:
            print(f"  seq={fix['seq']} ({fix['pa']}):")
            print(f"    标准编号：{fix['old_std_no']} → {fix['new_std_no']}")
            print(f"    内容：{fix['old_content'][:50]}... → {fix['new_content'][:50]}...")
            print()
    
    # 保存详细报告
    with open('/tmp/clauses_verify_report.json', 'w', encoding='utf-8') as f:
        json.dump({
            'stats': stats,
            'fixes': fixes,
            'pdf_clauses_summary': {pa: {'section': d['section'], 'count': len(d['bp_refs'])} 
                                   for pa, d in pdf_clauses.items()}
        }, f, ensure_ascii=False, indent=2)
    
    print(f"详细报告已保存到：/tmp/clauses_verify_report.json")

if __name__ == '__main__':
    main()
