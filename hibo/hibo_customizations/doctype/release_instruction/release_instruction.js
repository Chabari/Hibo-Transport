// Copyright (c) 2025, George Mukundi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Release Instruction", {
	refresh(frm) {
	},
    onload: function (frm) {
		frm.set_query("transporter", function () {
            return {
                filters: {
                    is_transporter: 1
                }
            };
        });

        frm.set_query("loadingsource_depot", function () {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        });

        frm.set_query("offload_depot", function () {
            return {
                filters: {
                    company: frm.doc.customer
                }
            };
        });

        frm.set_query("linked_sales_order", function () {
            return {
                filters: {
                    company: frm.doc.company
                }
            };
        });
	},

    transporter: function(frm){
		frm.doc.items.forEach(function (row) {
			frappe.model.set_value('Release Instruction Details', row.name, 'transporter', frm.doc.transporter);
		});
		frm.refresh_field('items');
	},

    offload_depot: function(frm){
		frm.doc.items.forEach(function (row) {
			frappe.model.set_value('Release Instruction Details', row.name, 'offload_depot', frm.doc.offload_depot);
		});
		frm.refresh_field('items');
	},

    batch_number: function(frm){
		frm.doc.items.forEach(function (row) {
			frappe.model.set_value('Release Instruction Details', row.name, 'batch_number', frm.doc.batch_number);
		});
		frm.refresh_field('items');
	},

    selling_price: function(frm){
		frm.doc.items.forEach(function (row) {
			frappe.model.set_value('Release Instruction Details', row.name, 'selling_price', frm.doc.selling_price);
		});
		frm.refresh_field('items');
	},
    

    before_workflow_action: async function(frm) {
        let required_fields = ["loaded_capacity20"];
        let missing_rows = [];

        frm.doc.items.forEach((row, index) => {
            let missing_fields = required_fields.filter(field => !row[field]);

            if (missing_fields.length > 0) {
                missing_rows.push(`Row ${index + 1}: Loaded Capacity @ 20`);
            }
        });

        if (missing_rows.length > 0) {

			frappe.throw("Please fill in the following fields before proceeding: <br><b>" + missing_rows.join("<br>") + "</b>");
        }

        try {
           
            let r = await frappe.call({
                method: "hibo.api.generate_delivery_note",
                freeze_message: __("Generating Delivery notes"),
                freeze: true,
                args: {
                    name: frm.doc.name
                },
                
            });

            if (r && r.message == true) {
                frappe.msgprint(__("Succes. Delivery notes for the vehicles have been generated."));
                frm.refresh();
                
            }else{
                frappe.throw(r.message);
            }
            
        } catch (error) {
            frappe.msgprint({
                title: __("Error"),
                message: __("An error occurred while validating the workflow."),
                indicator: "red"
            });

            frappe.validated = false;
            frappe.throw(error);
        }
        
    }
    
});

frappe.ui.form.on("Release Instruction Details", {
	
	items_add: function (frm, cdt, cdn) {
		var item = frappe.get_doc(cdt, cdn);
		if (!item.transporter && frm.doc.transporter) {
			frappe.model.set_value(cdt, cdn, "transporter", frm.doc.transporter);
		}
        if (!item.offload_depot && frm.doc.offload_depot) {
			frappe.model.set_value(cdt, cdn, "offload_depot", frm.doc.offload_depot);
		}
        if (!item.release_date && frm.doc.date) {
			frappe.model.set_value(cdt, cdn, "release_date", frm.doc.date);
		}
        if (!item.batch_number && frm.doc.batch_number) {
			frappe.model.set_value(cdt, cdn, "batch_number", frm.doc.batch_number);
		}

        if (!item.selling_price && frm.doc.selling_price) {
			frappe.model.set_value(cdt, cdn, "selling_price", frm.doc.selling_price);
		}

	},

});
