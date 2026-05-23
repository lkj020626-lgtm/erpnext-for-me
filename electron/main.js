const { app, BrowserWindow, Menu, dialog } = require("electron");
const path = require("path");
const fs = require("fs");

const CONFIG_PATH = path.join(app.getPath("userData"), "config.json");

let mainWindow;

function getServerUrl() {
  if (fs.existsSync(CONFIG_PATH)) {
    try {
      const config = JSON.parse(fs.readFileSync(CONFIG_PATH, "utf8"));
      if (config.serverUrl) return config.serverUrl;
    } catch (e) {}
  }
  return null;
}

function saveServerUrl(url) {
  fs.writeFileSync(CONFIG_PATH, JSON.stringify({ serverUrl: url }), "utf8");
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    title: "星造 StarMake ERP",
    icon: path.join(__dirname, "icon.png"),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  const serverUrl = getServerUrl();

  if (serverUrl) {
    mainWindow.loadURL(serverUrl);
  } else {
    showServerConfig();
  }

  const menu = Menu.buildFromTemplate([
    {
      label: "星造ERP",
      submenu: [
        {
          label: "配置服务器地址",
          click: showServerConfig,
        },
        { type: "separator" },
        {
          label: "刷新",
          accelerator: "F5",
          click: () => mainWindow.reload(),
        },
        {
          label: "开发者工具",
          accelerator: "F12",
          click: () => mainWindow.webContents.toggleDevTools(),
        },
        { type: "separator" },
        { label: "退出", accelerator: "Alt+F4", role: "quit" },
      ],
    },
  ]);
  Menu.setApplicationMenu(menu);

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

function showServerConfig() {
  const configHtml = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>配置服务器</title>
      <style>
        body {
          font-family: "Microsoft YaHei", sans-serif;
          display: flex; align-items: center; justify-content: center;
          height: 100vh; margin: 0; background: #f5f7fa;
        }
        .card {
          background: #fff; padding: 40px; border-radius: 12px;
          box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center;
          max-width: 400px; width: 90%;
        }
        h2 { color: #2196F3; margin-bottom: 8px; }
        p { color: #666; font-size: 14px; margin-bottom: 24px; }
        input {
          width: 100%; padding: 12px; font-size: 16px;
          border: 2px solid #e0e0e0; border-radius: 8px;
          box-sizing: border-box; margin-bottom: 16px;
        }
        input:focus { border-color: #2196F3; outline: none; }
        button {
          width: 100%; padding: 12px; font-size: 16px;
          background: #2196F3; color: #fff; border: none;
          border-radius: 8px; cursor: pointer;
        }
        button:hover { background: #1976D2; }
        .hint { font-size: 12px; color: #999; margin-top: 12px; }
      </style>
    </head>
    <body>
      <div class="card">
        <h2>星造 StarMake ERP</h2>
        <p>请输入 ERP 服务器地址</p>
        <input id="url" type="text" placeholder="http://192.168.1.100" autofocus>
        <button onclick="connect()">连接</button>
        <p class="hint">输入服务器的 IP 地址或域名，例如 http://192.168.1.100</p>
      </div>
      <script>
        function connect() {
          let url = document.getElementById('url').value.trim();
          if (!url) return alert('请输入服务器地址');
          if (!url.startsWith('http')) url = 'http://' + url;
          // Send to main process via URL hash
          window.location.href = 'about:blank#' + encodeURIComponent(url);
        }
        document.getElementById('url').addEventListener('keypress', (e) => {
          if (e.key === 'Enter') connect();
        });
      </script>
    </body>
    </html>
  `;

  mainWindow.loadURL(
    "data:text/html;charset=utf-8," + encodeURIComponent(configHtml)
  );

  mainWindow.webContents.on("did-navigate", (event, url) => {
    if (url.includes("about:blank#")) {
      const serverUrl = decodeURIComponent(url.split("#")[1]);
      saveServerUrl(serverUrl);
      mainWindow.loadURL(serverUrl);
    }
  });
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  app.quit();
});

app.on("activate", () => {
  if (mainWindow === null) createWindow();
});
