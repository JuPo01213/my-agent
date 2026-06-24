#!/usr/bin/env python3
"""
文档自动化系统 - 本地配置脚本

自动完成：
1. 检查 Python 版本
2. 安装依赖
3. 验证配置文件
4. 运行首次同步检查
5. 构建文档站点

用法：
    python setup_documentation.py
"""

import sys
import subprocess
import os
from pathlib import Path


def check_python_version():
    """检查 Python 版本。"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 版本过低，需要 Python 3.8+")
        print(f"   当前版本：{version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python 版本：{version.major}.{version.minor}.{version.micro}")
    return True


def install_dependencies():
    """安装依赖。"""
    print("\n📦 安装依赖...")
    
    # 优先使用项目虚拟环境
    root = Path(__file__).resolve().parent
    venv_python = root / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        python_cmd = str(venv_python)
        print(f"   检测到虚拟环境：{python_cmd}")
    else:
        python_cmd = sys.executable
        print(f"   使用系统 Python：{python_cmd}")
    
    packages = [
        "mkdocs-material",
        "mkdocs-minify-plugin",
        "pyyaml",
        "openai",
    ]
    
    for package in packages:
        print(f"   安装 {package}...")
        try:
            subprocess.run(
                [python_cmd, "-m", "pip", "install", package, "-q"],
                check=True,
                capture_output=True,
            )
            print(f"   ✅ {package}")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  {package} 安装失败：{e}")
            return False
    
    return True


def verify_configs():
    """验证配置文件。"""
    print("\n🔍 验证配置文件...")
    
    root = Path(__file__).resolve().parent
    
    # 检查 mkdocs.yml
    mkdocs_path = root / "mkdocs.yml"
    if not mkdocs_path.exists():
        print("   ❌ mkdocs.yml 不存在")
        return False
    print("   ✅ mkdocs.yml")
    
    # 检查 docs_sync/config.yaml
    config_path = root / "docs_sync" / "config.yaml"
    if not config_path.exists():
        print("   ❌ docs_sync/config.yaml 不存在")
        return False
    print("   ✅ docs_sync/config.yaml")
    
    # 检查 docs 目录
    docs_path = root / "docs"
    if not docs_path.exists():
        print("   ❌ docs/ 目录不存在")
        return False
    print("   ✅ docs/")
    
    return True


def run_sync_check():
    """运行同步检查。"""
    print("\n🔍 运行文档同步检查...")
    
    root = Path(__file__).resolve().parent
    script = root / ".github" / "skills" / "project-initializer" / "scripts" / "sync_checkpoint.py"
    
    if not script.exists():
        print("   ⚠️  sync_checkpoint.py 不存在，跳过")
        return True
    
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            check=False,
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode != 0:
            print("   ⚠️  同步检查发现警告（这不影响配置，但建议查看）")
            return True
        
        print("   ✅ 同步检查通过")
        return True
    except Exception as e:
        print(f"   ⚠️  运行检查失败：{e}")
        return True


def build_docs():
    """构建文档站点。"""
    print("\n🔨 构建文档站点...")
    
    root = Path(__file__).resolve().parent
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mkdocs", "build", "--strict"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        
        if result.returncode != 0:
            print("   ❌ 构建失败：")
            print(result.stderr)
            return False
        
        print("   ✅ 构建成功")
        print(f"   产物目录：{root / 'site'}")
        return True
    except Exception as e:
        print(f"   ❌ 构建失败：{e}")
        return False


def print_next_steps():
    """打印后续步骤。"""
    print("\n" + "=" * 60)
    print("🎉 本地配置完成！")
    print("=" * 60)
    
    print("\n📋 后续步骤：")
    print("\n1. 启用 GitHub Pages（需要手动操作）：")
    print("   - 打开 GitHub 仓库 → Settings → Pages")
    print("   - Source 选择：GitHub Actions")
    print("   - 保存后，推送代码即可自动部署")
    
    print("\n2. 配置 AI 文档审查（可选）：")
    print("   - 获取 StepFun API Key：https://platform.stepfun.com/")
    print("   - GitHub 仓库 → Settings → Secrets → Actions")
    print("   - 添加 Secret：STEPFUN_API_KEY = 你的 API Key")
    
    print("\n3. 本地预览文档：")
    print("   mkdocs serve")
    print("   然后访问：http://localhost:8000")
    
    print("\n4. 查看配置指南：")
    print("   docs/guides/documentation-setup.md")
    
    print("\n" + "=" * 60)


def main():
    print("=" * 60)
    print("文档自动化系统 - 配置向导")
    print("=" * 60)
    
    # 检查 Python 版本
    if not check_python_version():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        print("\n⚠️  依赖安装失败，请手动运行：")
        print("   pip install mkdocs-material mkdocs-minify-plugin pyyaml openai")
    
    # 验证配置
    if not verify_configs():
        print("\n❌ 配置文件验证失败")
        sys.exit(1)
    
    # 运行同步检查
    run_sync_check()
    
    # 构建文档
    build_docs()
    
    # 打印后续步骤
    print_next_steps()


if __name__ == "__main__":
    main()
