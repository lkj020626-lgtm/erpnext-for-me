# 星造 StarMake ERP

基于 ERPNext 的轻量级 ERP 系统，专为中小制造企业、贸易商和仓储企业设计。

## 特性

- 基于 ERPNext v15 + Frappe Framework，稳定可靠
- 覆盖采购、销售、库存、生产、财务、CRM 全流程
- 中文界面、中文打印模板、中文报表
- 私有化部署，数据完全自主可控
- 支持裸机部署和 Docker 部署
- 自动每日备份，30 天保留策略

## 快速开始

### Docker 部署（推荐）

```bash
git clone https://github.com/lkj020626-lgtm/erpnext-for-me.git
cd erpnext-for-me/deployment
cp .env.example .env
# 编辑 .env 设置密码
bash scripts/init.sh
```

### 裸机部署

参见 [docs/部署指南.md](docs/部署指南.md)

## 文档

| 文档 | 说明 |
|------|------|
| [部署指南](docs/部署指南.md) | 裸机 + Docker 完整部署流程 |
| [用户使用说明](docs/用户使用说明.md) | 各模块操作指南 |
| [管理员手册](docs/管理员手册.md) | 权限、备份、运维 |
| [二次开发说明](docs/二次开发说明.md) | 代码结构、扩展方式 |

## 模块概览

| 模块 | 功能 |
|------|------|
| 基础资料 | 商品、客户、供应商、仓库、分类 |
| 采购管理 | 采购订单、采购入库、供应商管理 |
| 销售管理 | 销售订单、销售出库、客户管理 |
| 库存管理 | 库存流水、预警、盘点、调拨 |
| 生产管理 | BOM、工单、领料、完工入库 |
| 财务管理 | 应收应付、收付款、对账单、毛利 |
| CRM/售后 | 客户跟进、售后工单、保修管理 |
| 报表中心 | 7+ 常用报表，支持筛选和导出 |
| 打印模板 | 7 种单据中文 A4 打印格式 |
| 系统管理 | 角色权限、自动备份、操作日志 |

## 技术栈

- Python 3.11+ / Frappe Framework
- MariaDB 10.11+
- Redis 7+
- Node.js 18+
- Nginx
- Docker / Docker Compose

## 许可证

GNU General Public License v3.0
