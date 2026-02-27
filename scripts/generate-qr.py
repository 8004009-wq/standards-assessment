#!/usr/bin/env python3
"""
生成访问二维码
使用方法：python3 generate-qr.py <访问地址>
"""

import sys
import os

# 尝试安装 qrcode
try:
    import qrcode
except ImportError:
    print("📦 正在安装 qrcode 库...")
    os.system("pip3 install qrcode[pil] -q")
    import qrcode

def generate_qr(url, output_path="/tmp/access_qr.png"):
    """生成二维码"""
    print(f"📱 生成访问二维码...")
    print(f"   地址：{url}")
    
    # 创建二维码
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # 生成图片
    img = qr.make_image(fill='black', back_color='white')
    img.save(output_path)
    
    print(f"✅ 二维码已生成：{output_path}")
    print(f"")
    print(f"使用方法:")
    print(f"  1. 将 {output_path} 发送到钉钉群")
    print(f"  2. 成员扫码即可访问")
    print(f"")
    
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法：python3 generate-qr.py <访问地址>")
        print("")
        print("示例:")
        print("  python3 generate-qr.py http://192.168.1.100:8080")
        print("  python3 generate-qr.py https://xxxxx.cpolar.cn")
        sys.exit(1)
    
    url = sys.argv[1]
    generate_qr(url)
