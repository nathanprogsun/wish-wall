.PHONY: help dev install clean backend frontend test lint format stop

# Default target
help:
	@echo "🎯 Wish Wall - 许愿墙项目管理"
	@echo ""
	@echo "🚀 快速启动:"
	@echo "  make dev              - 一键启动全栈服务 (后端先启动10秒)"
	@echo ""
	@echo "🔧 独立启动:"
	@echo "  make backend          - 启动后端开发服务"
	@echo "  make frontend         - 启动前端开发服务"
	@echo ""
	@echo "📦 项目管理:"
	@echo "  make install          - 安装所有依赖"
	@echo "  make clean            - 清理缓存和临时文件"
	@echo "  make test             - 运行所有测试"
	@echo "  make lint             - 代码检查"
	@echo "  make format           - 格式化代码"
	@echo "  make stop             - 停止所有服务"
	@echo ""
	@echo "🗄️  数据库管理:"
	@echo "  make db-init          - 初始化数据库"
	@echo "  make db-migrate       - 运行数据库迁移"
	@echo "  make db-seed          - 生成种子数据"
	@echo ""
	@echo "📊 项目信息:"
	@echo "  make status           - 查看服务状态"
	@echo "  make logs             - 查看服务日志"

# 🚀 一键启动 - 后端先启动10秒，再启动前端
dev:
	@echo "🚀 启动 Wish Wall 全栈应用..."
	@echo "📍 后端: http://localhost:8000"
	@echo "📍 前端: http://localhost:3000"
	@echo "📍 API文档: http://localhost:8000/api/docs"
	@echo ""
	@echo "🔧 正在启动后端服务..."
	@cd backend && poetry run python -m app &
	@echo "⏳ 等待后端服务启动 (10秒)..."
	@sleep 10
	@echo "🎨 正在启动前端服务..."
	@cd frontend && npm run dev

# 📦 安装所有依赖
install:
	@echo "📦 安装依赖..."
	@echo "  - 安装后端依赖 (Poetry)..."
	@cd backend && poetry install
	@echo "  - 安装前端依赖 (npm)..."
	@cd frontend && npm install
	@echo "✅ 依赖安装完成"

# 🧹 清理项目
clean:
	@echo "🧹 清理项目缓存..."
	@cd backend && poetry run python -c "import shutil; import os; [shutil.rmtree(d, ignore_errors=True) for d in ['.pytest_cache', '__pycache__', '.mypy_cache', '.ruff_cache']]"
	@cd frontend && rm -rf .next node_modules/.cache
	@echo "✅ 清理完成"

# 🔧 后端开发服务
backend:
	@echo "🔧 启动后端开发服务..."
	@echo "📍 后端服务: http://localhost:8000"
	@echo "📍 API文档: http://localhost:8000/api/docs"
	@echo ""
	@cd backend && poetry run python -m app

# 🎨 前端开发服务
frontend:
	@echo "🎨 启动前端开发服务..."
	@echo "📍 前端应用: http://localhost:3000"
	@echo ""
	@cd frontend && npm run dev

# 🗄️ 数据库管理
db-init:
	@echo "🗄️ 初始化数据库..."
	@cd backend && make migrations-init || true
	@cd backend && make migrations-upgrade || true

db-migrate:
	@echo "🗄️ 运行数据库迁移..."
	@cd backend && make migrations-upgrade

db-seed:
	@echo "🌱 生成种子数据..."
	@cd backend && make seed

# 🧪 测试
test:
	@echo "🧪 运行测试..."
	@echo "  - 后端测试..."
	@cd backend && make test
	@echo "  - 前端测试..."
	@cd frontend && npm run lint

# 🔍 代码检查
lint:
	@echo "🔍 代码检查..."
	@echo "  - 后端检查..."
	@cd backend && make lint
	@echo "  - 前端检查..."
	@cd frontend && npm run lint

# ✨ 代码格式化
format:
	@echo "✨ 格式化代码..."
	@echo "  - 后端格式化..."
	@cd backend && make format
	@echo "  - 前端格式化 (通过lint)..."
	@cd frontend && npm run lint

# 🛑 停止服务
stop:
	@echo "🛑 停止所有服务..."
	@pkill -f "python -m app" || true
	@pkill -f "next dev" || true
	@echo "✅ 所有服务已停止"

# 📊 状态检查
status:
	@echo "📊 服务状态检查..."
	@echo "🔧 后端服务 (端口 8000):"
	@lsof -i :8000 || echo "  ❌ 后端服务未运行"
	@echo "🎨 前端服务 (端口 3000):"
	@lsof -i :3000 || echo "  ❌ 前端服务未运行"

# 📜 查看日志
logs:
	@echo "📜 查看最近的日志..."
	@echo "🔧 后端日志:"
	@cd backend && find logs -name "*.log" -exec tail -n 10 {} \; 2>/dev/null || echo "  ℹ️  暂无后端日志"
	@echo "🎨 前端日志:"
	@echo "  ℹ️  前端日志在控制台输出" 