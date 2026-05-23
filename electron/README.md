# 星造 StarMake ERP 桌面客户端

将 StarMake ERP 打包为 Windows/Linux/Mac 桌面应用程序。

## 原理

本质是一个 Electron 壳，内部加载 ERP 服务器的网页。
客户双击桌面图标即可使用，不需要手动打开浏览器输入地址。

## 构建步骤

### 1. 安装依赖

```bash
cd electron
npm install
```

### 2. 开发测试

```bash
npm start
```

启动后会弹出配置窗口，输入服务器地址即可连接。

### 3. 打包为安装程序

```bash
# Windows .exe 安装包
npm run build:win

# Linux AppImage
npm run build:linux

# macOS .dmg
npm run build:mac
```

产出文件在 `electron/dist/` 目录。

## 使用方式

1. 将打包好的 .exe 发给客户
2. 客户双击安装
3. 首次打开输入服务器 IP（如 `192.168.1.100`）
4. 之后每次打开自动连接，无需重复输入

## 自定义

- 修改 `package.json` 中的 `productName` 改应用名称
- 替换 `icon.ico` / `icon.png` 改应用图标
- 修改 `main.js` 中的窗口大小、菜单等
