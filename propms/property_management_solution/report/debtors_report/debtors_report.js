frappe.query_reports["Debtors Report"] = {
    "formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
        console.log(column)
        if (column.id == "usd") {
            value = "<span style='float:right;'>" + value + "</span>";
        }

        if (data["items"] == "TOTAL"){
            value = "<span style='font-weight:bold;'>" + value + "</span>";
            if (column.id == "due_date"){
                value = ""
            }
            if (column.id == "from_date") {
              value = "";
            }
            if (column.id == "to_date") {
              value = "";
            }
         }

        return value;
    }
}