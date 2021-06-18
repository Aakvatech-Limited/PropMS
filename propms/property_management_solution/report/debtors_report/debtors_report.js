frappe.query_reports["Debtors Report"] = {
  filters: [
  ],
  formatter: function (value, row, column, data, default_formatter) {
    value = default_formatter(value, row, column, data);
    // console.log(column)
    if (column.id == "usd") {
      value = "<span style='float:right;'>" + value + "</span>";
    }
    if (column.id == "tzs") {
      value = "<span style='float:right;'>" + value + "</span>";
    }

    if (data["invoice_no"] == "TOTAL") {
      value = "<span style='font-weight:bold;'>" + value + "</span>";
      if (column.id == "due_date") {
        value = "";
      }

      if (column.id == "cost_center") {
        value = "";
      }

      if (column.id == "items") {
        value = "";
      }
      if (column.id == "from_date") {
        value = "";
      }
      if (column.id == "to_date") {
        value = "";
      }
    }

    return value;
  },
};