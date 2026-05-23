// StarMake - Lightweight ERP Extensions
// UI simplification + Chinese defaults + PWA + import/export buttons

frappe.provide("starmake");

// ============================================================
// PWA: 注册 Service Worker + Manifest
// ============================================================
if ("serviceWorker" in navigator) {
  navigator.serviceWorker
    .register("/assets/starmake/pwa/sw.js")
    .catch(() => {});
}
(function () {
  if (!document.querySelector('link[rel="manifest"]')) {
    const link = document.createElement("link");
    link.rel = "manifest";
    link.href = "/assets/starmake/pwa/manifest.json";
    document.head.appendChild(link);
  }
  const meta = document.createElement("meta");
  meta.name = "theme-color";
  meta.content = "#2196F3";
  document.head.appendChild(meta);
})();

// ============================================================
// 新手友好：简化桌面快捷入口
// ============================================================
$(document).on("app_ready", function () {
  // 强制设置语言为中文（如果还没设置）
  if (frappe.boot && frappe.boot.lang !== "zh") {
    frappe.call({
      method: "frappe.client.set_value",
      args: {
        doctype: "User",
        name: frappe.session.user,
        fieldname: "language",
        value: "zh",
      },
      async: true,
    });
  }

  // 在桌面添加快捷操作卡片
  if (
    frappe.get_route_str() === "" ||
    frappe.get_route_str() === "Workspaces"
  ) {
    starmake.add_quick_actions();
  }
});

starmake.add_quick_actions = function () {
  if (document.querySelector(".starmake-quick-actions")) return;

  const actions = [
    { label: "新建销售订单", route: "/app/sales-order/new", icon: "📋" },
    { label: "新建采购订单", route: "/app/purchase-order/new", icon: "🛒" },
    { label: "库存查询", route: "/app/query-report/Current Stock Report", icon: "📦" },
    { label: "新建商品", route: "/app/item/new", icon: "🏷️" },
    { label: "低库存预警", route: "/app/query-report/Low Stock Warning", icon: "⚠️" },
    { label: "销售报表", route: "/app/query-report/Sales Summary", icon: "📊" },
  ];

  let html = `<div class="starmake-quick-actions sm-animate">
    <h5><span class="starmake-gradient-text">常用操作</span></h5>
    <div style="display: flex; flex-wrap: wrap; gap: 12px; position: relative; z-index: 1;">`;

  actions.forEach((a, i) => {
    html += `<a href="${a.route}" class="btn btn-default btn-sm sm-animate" style="
      animation-delay: ${i * 0.08}s;
    ">${a.icon} ${a.label}</a>`;
  });

  html += `</div></div>`;

  setTimeout(() => {
    const container = document.querySelector(".layout-main-section");
    if (container && !document.querySelector(".starmake-quick-actions")) {
      container.insertAdjacentHTML("afterbegin", html);
      starmake.init_scroll_animations();
    }
  }, 800);
};

// ============================================================
// 简化侧边栏：隐藏小工厂不需要的模块
// ============================================================
$(document).on("app_ready", function () {
  const hide_modules = ["Quality Management", "EDI", "Subcontracting"];

  setTimeout(() => {
    hide_modules.forEach((mod) => {
      document
        .querySelectorAll(`[data-module="${mod}"], [data-module-name="${mod}"]`)
        .forEach((el) => {
          const parent = el.closest("li") || el.closest(".module-link");
          if (parent) parent.style.display = "none";
        });
    });
  }, 2000);
});

// ============================================================
// Excel 导入导出按钮
// ============================================================
starmake.add_import_buttons = function (listview, doctype) {
  listview.page.add_inner_button(__("下载导入模板"), function () {
    window.open(
      `/api/method/starmake.master_data.excel_template.download_template?doctype=${doctype}`
    );
  }, __("Excel"));

  listview.page.add_inner_button(__("批量导入"), function () {
    starmake.show_import_dialog(doctype);
  }, __("Excel"));
};

starmake.show_import_dialog = function (doctype) {
  let d = new frappe.ui.Dialog({
    title: __("批量导入 {0}", [__(doctype)]),
    fields: [
      {
        fieldtype: "HTML",
        options: `<p class="text-muted">请先下载模板，按模板格式填写数据后上传。黄色底色列为必填。</p>`,
      },
      {
        fieldname: "import_file",
        fieldtype: "Attach",
        label: __("选择 Excel 文件"),
        reqd: 1,
        options: { restrictions: { allowed_file_types: [".xlsx", ".xls"] } },
      },
    ],
    primary_action_label: __("开始导入"),
    primary_action: function (values) {
      if (!values.import_file) {
        frappe.msgprint(__("请选择文件"));
        return;
      }
      d.hide();
      frappe.call({
        method: "starmake.master_data.import_export.import_records",
        args: { doctype: doctype, file_url: values.import_file },
        freeze: true,
        freeze_message: __("正在导入..."),
        callback: function (r) {
          if (r.message) {
            let msg = __("导入完成：成功 {0} 条，失败 {1} 条", [
              r.message.success,
              r.message.failed,
            ]);
            if (r.message.errors && r.message.errors.length) {
              msg += "<br><br><b>错误详情：</b><ul>";
              r.message.errors.forEach(function (e) {
                msg += `<li>第 ${e.row} 行：${e.error}</li>`;
              });
              msg += "</ul>";
            }
            frappe.msgprint({
              title: __("导入结果"),
              message: msg,
              indicator: "blue",
            });
            cur_list.refresh();
          }
        },
      });
    },
  });
  d.show();
};

// ============================================================
// 列表页扩展
// ============================================================
const _item_list_onload = frappe.listview_settings["Item"]
  ? frappe.listview_settings["Item"].onload
  : null;

frappe.listview_settings["Item"] = frappe.listview_settings["Item"] || {};
frappe.listview_settings["Item"].onload = function (listview) {
  if (_item_list_onload) _item_list_onload(listview);
  starmake.add_import_buttons(listview, "Item");
};

const _customer_list_onload = frappe.listview_settings["Customer"]
  ? frappe.listview_settings["Customer"].onload
  : null;

frappe.listview_settings["Customer"] = frappe.listview_settings["Customer"] || {};
frappe.listview_settings["Customer"].onload = function (listview) {
  if (_customer_list_onload) _customer_list_onload(listview);
  starmake.add_import_buttons(listview, "Customer");
};

const _supplier_list_onload = frappe.listview_settings["Supplier"]
  ? frappe.listview_settings["Supplier"].onload
  : null;

frappe.listview_settings["Supplier"] =
  frappe.listview_settings["Supplier"] || {};
frappe.listview_settings["Supplier"].onload = function (listview) {
  if (_supplier_list_onload) _supplier_list_onload(listview);
  starmake.add_import_buttons(listview, "Supplier");
};

// ============================================================
// Scroll Animations (IntersectionObserver)
// ============================================================
starmake.init_scroll_animations = function () {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("sm-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 }
  );

  document
    .querySelectorAll(".sm-animate, .sm-animate-left, .sm-animate-scale")
    .forEach((el) => observer.observe(el));
};

// Run on every page change
$(document).on("page-change", function () {
  setTimeout(starmake.init_scroll_animations, 500);
});

// ============================================================
// Click Spark Effect (subtle particle burst on button clicks)
// ============================================================
$(document).on("click", ".btn-primary, .btn-primary-dark", function (e) {
  const btn = e.currentTarget;
  const rect = btn.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  for (let i = 0; i < 6; i++) {
    const spark = document.createElement("span");
    spark.className = "sm-spark";
    spark.style.left = x + "px";
    spark.style.top = y + "px";
    spark.style.setProperty("--angle", Math.random() * 360 + "deg");
    spark.style.setProperty("--distance", 20 + Math.random() * 30 + "px");
    btn.style.position = "relative";
    btn.style.overflow = "hidden";
    btn.appendChild(spark);
    setTimeout(() => spark.remove(), 600);
  }
});
