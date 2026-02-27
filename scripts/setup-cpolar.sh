#!/bin/bash

# cpolar 内网穿透安装脚本
# 使用方法：bash setup-cpolar.sh <your-cpolar-token>

echo "============================================================"
echo "🚀 cpolar 内网穿透安装脚本"
echo "============================================================"
echo ""

# 检查参数
if [ -z "$1" ]; then
    echo "❌ 请提供 cpolar token"
    echo ""
    echo "使用方法:"
    echo "  bash setup-cpolar.sh <your-token>"
    echo ""
    echo "获取 token:"
    echo "  1. 访问 https://www.cpolar.com/"
    echo "  2. 注册账号"
    echo "  3. 在个人中心获取 token"
    echo ""
    exit 1
fi

CPOLAR_TOKEN=$1

# 检查是否已安装
if command -v cpolar &> /dev/null; then
    echo "✅ cpolar 已安装"
else
    echo "📦 正在下载 cpolar..."
    
    # 下载 cpolar
    cd /tmp
    wget -q https://static.cpolar.com/downloads/cpolar-linux-amd64.zip -O cpolar.zip
    
    if [ ! -f cpolar.zip ]; then
        echo "❌ 下载失败，请检查网络连接"
        echo ""
        echo "或者手动下载："
        echo "  访问：https://www.cpolar.com/download"
        echo "  选择：Linux AMD64"
        exit 1
    fi
    
    # 解压
    unzip -q cpolar.zip
    sudo mv cpolar /usr/local/bin/
    sudo chmod +x /usr/local/bin/cpolar
    
    echo "✅ cpolar 安装完成"
fi

# 配置 token
echo "🔑 配置认证 token..."
cpolar authtoken $CPOLAR_TOKEN

# 启动隧道
echo "🚀 启动内网穿透隧道..."
echo ""
echo "============================================================"
echo "正在将 8080 端口暴露到公网..."
echo "============================================================"
echo ""
echo "稍后会显示公网访问地址，格式类似："
echo "  http://xxxxx.cpolar.cn"
echo "  https://xxxxx.cpolar.cn"
echo ""
echo "将该地址发送到钉钉即可访问！"
echo "============================================================"
echo ""

# 启动 cpolar
cpolar http 8080
