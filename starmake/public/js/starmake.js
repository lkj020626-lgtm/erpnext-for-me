// StarMake - Lightweight ERP Extensions
// Adds import/export buttons to Item, Customer, Supplier list views

frappe.provide("starmake");

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
            frappe.msgprint({ title: __("导入结果"), message: msg, indicator: "blue" });
            cur_list.refresh();
          }
        },
      });
    },
  });
  d.show();
};

// Hook into list views
$(document).on("app_ready", function () {
  if (frappe.route_hooks) {
    frappe.route_hooks.after_load = frappe.route_hooks.after_load || [];
  }
});

// Extend Item List
const _item_list_onload = frappe.listview_settings["Item"]
  ? frappe.listview_settings["Item"].onload
  : null;

frappe.listview_settings["Item"] = frappe.listview_settings["Item"] || {};
frappe.listview_settings["Item"].onload = function (listview) {
  if (_item_list_onload) _item_list_onload(listview);
  starmake.add_import_buttons(listview, "Item");
};

// Extend Customer List
const _customer_list_onload = frappe.listview_settings["Customer"]
  ? frappe.listview_settings["Customer"].onload
  : null;

frappe.listview_settings["Customer"] = frappe.listview_settings["Customer"] || {};
frappe.listview_settings["Customer"].onload = function (listview) {
  if (_customer_list_onload) _customer_list_onload(listview);
  starmake.add_import_buttons(listview, "Customer");
};

// Extend Supplier List
const _supplier_list_onload = frappe.listview_settings["Supplier"]
  ? frappe.listview_settings["Supplier"].onload
  : null;

frappe.listview_settings["Supplier"] = frappe.listview_settings["Supplier"] || {};
frappe.listview_settings["Supplier"].onload = function (listview) {
  if (_supplier_list_onload) _supplier_list_onload(listview);
  starmake.add_import_buttons(listview, "Supplier");
};
