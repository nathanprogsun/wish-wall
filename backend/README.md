# Wish Wall - 许愿墙

一个美好的许愿墙应用，让梦想成真。

## 📁 项目结构

```
wish-wall/
├── backend/                # 后端服务 (Flask + SQLAlchemy)
│   ├── app/               # 应用核心代码
│   │   ├── model/         # 数据模型
│   │   ├── route/         # API路由
│   │   ├── service/       # 业务逻辑
│   │   ├── schema/        # 数据验证模式
│   │   ├── common/        # 通用模块
│   │   ├── util/          # 工具函数
│   │   └── data/          # 数据处理
│   ├── migrations/        # 数据库迁移文件
│   ├── scripts/           # 辅助脚本
│   ├── tests/             # 测试文件
│   ├── pyproject.toml     # Python项目配置
│   ├── poetry.lock        # 依赖锁定文件
│   ├── Makefile          # 构建和管理命令
│   └── alembic.ini       # 数据库迁移配置
├── frontend/              # 前端应用 (Next.js + React)
│   ├── src/              # 源代码
│   │   ├── components/    # React组件
│   │   ├── pages/        # 页面组件
│   │   ├── lib/          # 库文件
│   │   ├── utils/        # 工具函数
│   │   ├── contexts/     # React上下文
│   │   └── styles/       # 样式文件
│   ├── public/           # 静态资源
│   ├── package.json      # Node.js项目配置
│   └── next.config.js    # Next.js配置
├── scripts/              # 项目级脚本
├── README.md            # 项目说明
└── .gitignore           # Git忽略文件配置
```

## 🚀 快速启动

### 前置要求

- Python 3.12+
- Poetry (Python包管理器)
- Node.js 18+
- npm 或 yarn

### 首次使用（推荐）

```bash
# 初始化开发环境
./scripts/setup.sh

# 启动前后端服务
make dev
```

### 一键启动

```bash
# 启动前后端服务
make dev

# 或者使用脚本
./scripts/start.sh
```

### 分别启动

#### 后端启动

```bash
cd backend
poetry install          # 安装依赖
poetry run python -m app # 启动后端服务
```

后端将在 `http://localhost:8000` 启动

#### 前端启动

```bash
cd frontend
npm install    # 安装依赖
npm run dev    # 启动开发服务器
```

前端将在 `http://localhost:3000` 启动

## 🛠️ 开发命令

### 后端命令 (在 backend/ 目录下)

```bash
make help                # 查看所有可用命令

# 代码质量
make format             # 格式化代码
make lint               # 代码检查
make quality            # 运行所有质量检查

# 测试
make test               # 运行所有测试
make test-unit          # 运行单元测试
make test-api           # 运行API测试

# 数据库
make migrations-generate MSG='描述'  # 生成迁移
make migrations-upgrade              # 应用迁移
make migrations-downgrade            # 回滚迁移
make seed                           # 生成种子数据

# 开发
make dev                # 启动开发服务器
```

### 前端命令 (在 frontend/ 目录下)

```bash
npm run dev      # 启动开发服务器
npm run build    # 构建生产版本
npm run start    # 启动生产服务器
npm run lint     # 代码检查
```

## 🏗️ 技术栈

### 后端
- **框架**: Flask
- **数据库**: SQLAlchemy ORM
- **迁移**: Alembic
- **验证**: Pydantic
- **测试**: pytest
- **代码质量**: ruff, mypy
- **文档**: Flasgger (Swagger)

### 前端
- **框架**: Next.js 15
- **UI库**: React 18
- **样式**: Tailwind CSS
- **组件**: Radix UI
- **表单**: React Hook Form + Zod
- **HTTP**: Axios
- **类型检查**: TypeScript

## 📝 API文档

后端启动后，访问 `http://localhost:8000/api/docs` 查看Swagger API文档。

## 🔧 配置

### 后端配置
复制 `backend/.env.example` 到 `backend/.env` 并根据需要修改配置。

### 前端配置
根据需要修改 `frontend/next.config.js` 和环境变量。

## 📄 许可证

本项目采用 MIT 许可证。 