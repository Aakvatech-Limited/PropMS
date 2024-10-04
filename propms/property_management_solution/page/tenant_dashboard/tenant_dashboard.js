frappe.pages['tenant-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Tenant Dashboard',
        single_column: true
    });

    // Render main HTML template
    page.main.html(frappe.render_template("tenant_dashboard", {}));
    page.add_action_item('Service Request', () => open_service_request_dialog());
    page.add_action_item('Online Payment', () => refresh());
    let $btn = page.set_secondary_action('Download', () => download_data())

    // Function to open the Service Request dialog (moved from set_primary_action)
    function open_service_request_dialog() {
        let d = new frappe.ui.Dialog({
            title: 'Service Request Details',
            fields: [
                {
                    label: 'Service',
                    fieldname: 'service',
                    fieldtype: 'Link',
                    options: 'Item',
                    get_query: function() {
                        return {
                            filters: {
                                'item_group': 'Services'
                            }
                        };
                    }
                },
                {
                    label: 'Description',
                    fieldname: 'description',
                    fieldtype: 'Small Text'
                },
                {
                    label: 'Service Date',
                    fieldname: 'service_date',
                    fieldtype: 'Date'
                }
            ],
            primary_action_label: 'Submit',
            primary_action(values) {
                console.log(values);

                // Validate form fields (optional but recommended)
                if (!values.service || !values.service_date || !values.description) {
                    frappe.msgprint(__('Please fill out all fields before submitting.'));
                    return;
                }

                frappe.call({
                    method: 'propms.property_management_solution.page.tenant_dashboard.tenant_dashboard.create_service',
                    args: {
                        service: values.service,
                        description: values.description,
                        service_date: values.service_date
                    },
                    callback: (r) => {
                        if (r.message === 'success') {
                            frappe.show_alert({
                                message: ('Hi, Service request created successfully.'),
                                indicator: 'green'
                            }, 5);
                        } else {
                            frappe.throw(__('There was an issue creating the service request.'));
                        }
                    },
                    error: (r) => {
                        frappe.throw(__('An error occurred while creating the service request.'));
                    }
                });
                d.hide();
            }
        });

        d.show();
    }

    function download_data() {
        frappe.call({
            method: 'propms.property_management_solution.page.tenant_dashboard.tenant_dashboard.payments_history',
            callback: (response) => {download_data
                let payments_history = response.message;
                let csvContent = "data:text/csv;charset=utf-8,";
                csvContent += "Invoice Number, Date to Invoice, Lease Item Name, Rate, Currency\n"; // CSV Headers
                
                // Convert the payments history to CSV format
                payments_history.forEach((payment) => {
                    let row = [
                        payment.invoice_number || '-',
                        payment.date_to_invoice || '-',
                        payment.lease_item_name || '-',
                        payment.rate ? payment.rate.toLocaleString() : '-',
                        payment.currency || '-'
                    ];
                    csvContent += row.join(",") + "\n";
                });

                // Create a link element for download
                var encodedUri = encodeURI(csvContent);
                var link = document.createElement("a");
                link.setAttribute("href", encodedUri);
                link.setAttribute("download", "payments_history.csv");
                document.body.appendChild(link); // Required for Firefox

                // Trigger the download
                link.click();

                // Remove the link element after triggering download
                document.body.removeChild(link);
            }
        });
    }


    // Fetch user data
    frappe.call({
        method: 'propms.property_management_solution.page.tenant_dashboard.tenant_dashboard.get_role_info',
        callback: (r) => {
            let user = r.message;
            $("#user-image").attr("src", user.user_image);
            $("#user-name").text(user.full_name);
            $("#user-email").text(user.email || "-");
            $("#user-location").text(user.location || "-");
            $("#user-phone").text(user.phone || "-");
            $("#user-username").text(user.username || "-");
            $("#user-gender").text(user.gender || "-");
        },
        error: (r) => {
            console.error("Error fetching user data:", r);
        }
    });

    // Fetch balances
    frappe.call({
        method: 'propms.property_management_solution.page.tenant_dashboard.tenant_dashboard.balances',
        callback: (response) => {
            let lease = response.message;

            let upcomingRent = lease.upcoming_rent ? lease.upcoming_rent.toLocaleString() : "-";
            let allUpcomingRent = lease.all_upcoming_rent ? lease.all_upcoming_rent.toLocaleString() : "-";

            $("#upcoming_rent").text(upcomingRent);
            $("#all_upcoming_rent").text(allUpcomingRent);
            $("#lease_item_names").text(lease.lease_item_names || "-");
            $("#currency").text(lease.currency || "-");
            $("#currency2").text(lease.currency2 || "-");

            // console.log(upcomingRent, allUpcomingRent);
        }
    });

    // Fetch payment history
    frappe.call({
        method: 'propms.property_management_solution.page.tenant_dashboard.tenant_dashboard.payments_history',
        callback: (response) => {
            let payments_history = response.message;
            // console.log(payments_history);

            let tableBody = document.getElementById('payments-history-body');
            tableBody.innerHTML = "";

            payments_history.forEach((payment) => {
                let row = document.createElement('tr');
                row.innerHTML = `
                    <td>${payment.invoice_number || '-'}</td>
                    <td>${payment.date_to_invoice || '-'}</td>
                    <td>${payment.lease_item_name || '-'}</td>
                    <td>${payment.rate ? payment.rate.toLocaleString() : '-'}</td>
                    <td>${payment.currency || '-'}</td>
                `;
                tableBody.appendChild(row);
            });
        }
    });
};
