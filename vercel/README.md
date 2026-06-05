# 中考志愿智能填报 - Vercel 部署指南

## 快速部署（5分钟）

### 第1步：注册智谱AI并获取API Key

1. 访问 https://open.bigmodel.cn
2. 手机号注册 → 实名认证
3. 进入「API Keys」→ 创建新的 API Key → 复制保存

### 第2步：部署到 Vercel

**方式一：Vercel CLI（推荐）**
```bash
# 安装 Vercel CLI（一次性）
npm i -g vercel

# 进入项目目录
cd vercel-zhongkao

# 部署
vercel

# 按提示操作：
# - 登录 GitHub 账号
# - 选择项目
# - 部署完成后，设置环境变量

# 设置环境变量（API Key）
vercel env add ZHIPU_API_KEY
# 粘贴你的智谱 API Key
```

**方式二：Vercel 网页端**
1. 访问 https://vercel.com/import
2. 导入这个目录（或关联 GitHub 仓库）
3. 在 Settings → Environment Variables 添加：
   - Key: `ZHIPU_API_KEY`
   - Value: 你的智谱 API Key
4. 点 「Redeploy」

### 第3步：访问使用

部署完成后访问 Vercel 分配的域名（如 `xxx.vercel.app`），填入学生成绩即可生成方案。

## 本地测试（可选）

```bash
cd vercel-zhongkao
vercel dev
# 访问 http://localhost:3000
```

## 安全提示

- API Key 只存储在 Vercel 环境变量中，不会暴露给前端
- GLM-4-Flash 永久免费，30并发，适合个人项目
- 生产环境建议加验证码防止滥用
