# 智能体设计模式


## 项目介绍

本项目是一个智能体设计模式的示例，展示了如何使用智能体设计模式来实现智能体的开发。

## 环境配置

创建一个虚拟环境，用于安装项目依赖。

```bash
# 1. 创建虚拟环境（会在当前目录生成 venv 文件夹）
python -m venv .venv

# 2. 激活虚拟环境
## mac/linux 激活虚拟环境
source .venv/bin/activate

## windows 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 3. 确认已激活（命令行前缀会出现 (venv)） 
python --version 
which python 

# 4. 安装项目依赖（使用清华源加速）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 5. 退出虚拟环境 
deactivate
```

## 案例内容

### 1.提示链
