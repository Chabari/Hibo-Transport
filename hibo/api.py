import frappe
from erpnext.controllers.accounts_controller import get_taxes_and_charges, merge_taxes
from frappe.utils import flt, cint, getdate, get_datetime, nowdate, nowtime, add_days, unique, month_diff

from frappe.contacts.doctype.address.address import get_company_address
from frappe.model.utils import get_fetch_values
from frappe.model.mapper import get_mapped_doc
from frappe import _

def create_order(doc, method):
    if doc.company != doc.custom_target_company:
        # posting_date = nowdate()
        # posting_time = nowtime()
        
        _sales_order = frappe.db.get_value('Sales Order', {'po_no': doc.name}, ['name'], as_dict=1) 
        if not _sales_order:
            sales_order = frappe.new_doc("Sales Order")
            sales_order.po_no = doc.name
            sales_order.naming_series = "SAL-ORD-.YYYY.-"
        else:
            sales_order = frappe.get_doc("Sales Order", _sales_order.name)
            
        _customer = frappe.db.get_value('Customer', {'customer_name': doc.company}, ['name'], as_dict=1) 
        if not _customer:
            customer = frappe.new_doc("Customer")
            customer.customer_name = doc.company
            customer.customer_type = "Company"
            customer.save()
        else:
            customer = frappe.get_doc("Customer", _customer.name)
        
        sales_order.company = doc.custom_target_company
        sales_order.transaction_date = doc.transaction_date
        sales_order.delivery_date = doc.transaction_date
        sales_order.po_date = doc.transaction_date
        sales_order.order_type = "Sales"
        sales_order.customer = customer.name
        
        order_items = []
            
        for itm in doc.items:
            order_items.append(frappe._dict({
                'item_code': itm.get('item_code'),
                'item_name': itm.get('item_name'),
                'schedule_date': itm.get('schedule_date'),
                'delivery_date': itm.get('schedule_date'),
                'conversion_factor': 1,
                'qty': itm.get('qty'),
                "rate": itm.get('rate'),
                'uom': itm.get('uom')
            }))
        
        sales_order.set("items", order_items)
        sales_order.set_missing_values()
        
        sales_order.save(ignore_permissions=True)
        
def create_s_p_invoice(doc, method):
    if doc.transporter:
        posting_date = nowdate()
        posting_time = nowtime()
        _purchase_invoice = frappe.db.get_value('Purchase Invoice', {'custom_delivery_note_number': doc.name}, ['name'], as_dict=1) 
        if _purchase_invoice:
            purchase_invoice = frappe.get_doc("Purchase Invoice", _purchase_invoice.name)
        else:
            purchase_invoice = frappe.new_doc("Purchase Invoice")
            purchase_invoice.naming_series = "ACC-PINV-.YYYY.-"
            purchase_invoice.custom_delivery_note_number = doc.name
            
        purchase_invoice.supplier = doc.transporter
        purchase_invoice.company = doc.company
        purchase_invoice.posting_date = posting_date
        purchase_invoice.posting_time = posting_time
        purchase_invoice.set_posting_time = 1
        p_items = []
        transport_amount = frappe.get_all("Transport Setting", fields=["transport_amount"], limit=1)
        
        for itm in doc.items:
            qty = (itm.qty / 1000)
            p_items.append(frappe._dict({
                'item_code': "TRANSPORT SERVICE",
                'item_name': "TRANSPORT SERVICE",
                'description': f"TRANSPORT SERVICE - FOR {itm.item_name.upper()}",
                'received_qty': qty,
                'conversion_factor': 1,
                'qty': qty,
                "rate": transport_amount[0].transport_amount,
                'uom': "Cubic Meter",
                'stock_qty': qty
            }))
        
        purchase_invoice.set("items", p_items)
        
        purchase_invoice.flags.ignore_permissions = True
        frappe.flags.ignore_account_permission = True
        purchase_invoice.set_missing_values()
        purchase_invoice.save(ignore_permissions=True)
        
def create_c_i_invoice(doc, method):
    if doc.po_no:
        posting_date = nowdate()
        posting_time = nowtime()
        _purchase_invoice = frappe.db.get_value('Purchase Invoice', {'custom_linked_sales_invoice': doc.name}, ['name'], as_dict=1) 
        if _purchase_invoice:
            purchase_invoice = frappe.get_doc("Purchase Invoice", _purchase_invoice.name)
        else:
            purchase_invoice = frappe.new_doc("Purchase Invoice")
            purchase_invoice.naming_series = "ACC-PINV-.YYYY.-"
            purchase_invoice.custom_linked_sales_invoice = doc.name
            purchase_invoice.bill_no = doc.name
            purchase_invoice.bill_date = posting_date
          
        _supplier = frappe.db.get_value('Supplier', {'supplier_name': doc.company}, ['name'], as_dict=1) 
        if not _supplier:
            supplier = frappe.new_doc("Supplier")
            supplier.supplier_name = doc.company
            supplier.supplier_type = "Company"
            supplier.save()
        else:
            supplier = frappe.get_doc("Supplier", _supplier.name)
        
        purchase_invoice.supplier = supplier.name
        purchase_invoice.posting_date = posting_date
        purchase_invoice.posting_time = posting_time
        purchase_invoice.set_posting_time = 1
        purchase_invoice.company = doc.customer
        
        # .................
        
        _purchase_receipt = frappe.db.get_value('Purchase Receipt', {'custom_linked_sales_invoice': doc.name}, ['name'], as_dict=1) 
        if _purchase_receipt:
            purchase_receipt = frappe.get_doc("Purchase Receipt", _purchase_receipt.name)
        else:
            purchase_receipt = frappe.new_doc("Purchase Receipt")
            purchase_receipt.naming_series = "MAT-PRE-.YYYY.-"
            purchase_receipt.custom_linked_sales_invoice = doc.name
             
        purchase_receipt.supplier = supplier.name
        purchase_receipt.posting_date = posting_date
        purchase_receipt.posting_time = posting_time
        purchase_receipt.set_posting_time = 1
        purchase_receipt.company = doc.customer
        lpo = frappe.get_doc("Purchase Order", doc.po_no)
        purchase_receipt.set_warehouse = lpo.set_warehouse
        p_items = []
        pr_items = []
        
        _delivery_note = None
        
        transport_setting = frappe.get_all("Transport Setting", fields=["allowable_loss"], limit=1)
        
        for itm in doc.items:
            _delivery_note = itm.delivery_note
            delivery_note_item = frappe.get_doc("Delivery Note Item", itm.dn_detail)
            p_items.append(frappe._dict({
                'item_code': itm.item_code,
                'item_name': itm.item_name,
                'description': f"{itm.item_code} - FOR {itm.item_name.upper()}",
                'received_qty': itm.qty,
                'conversion_factor': 1,
                'qty': itm.qty,
                "rate": itm.rate,
                'uom': itm.uom,
                'stock_qty': itm.qty
            }))
            allowable_loss = (transport_setting[0].allowable_loss / 100) * itm.qty
            pr_items.append(frappe._dict({
                'item_code': itm.item_code,
                'item_name': itm.item_name,
                'description': f"{itm.item_code} - FOR {itm.item_name.upper()}",
                'received_qty': itm.qty,
                'conversion_factor': 1,
                'use_serial_batch_fields': 1,
                'qty': itm.qty,
                "rate": itm.rate,
                'uom': itm.stock_uom,
                'stock_uom': itm.stock_uom,
                'received_qty': itm.qty,
                'custom_offloaded_qty20': itm.qty,
                'custom_loaded_quantity': itm.qty,
                'custom_shortage': 0,
                'custom_allowable_loss': allowable_loss,
                'batch_no': delivery_note_item.batch_no,
                'serial_no': delivery_note_item.serial_no,
            }))
            
        purchase_receipt.supplier_delivery_note = _delivery_note
        
        purchase_invoice.set("items", p_items)
        purchase_invoice.flags.ignore_permissions = True
        purchase_invoice.set_missing_values()
        purchase_invoice.save(ignore_permissions=True)
        
        purchase_receipt.set("items", pr_items)
        purchase_receipt.custom_linked_purchase_invoice = purchase_invoice.name
        purchase_receipt.flags.ignore_permissions = True
        purchase_receipt.set_missing_values()
        purchase_receipt.save(ignore_permissions=True)
        
        frappe.flags.ignore_account_permission = True
        purchase_invoice.submit()

def create_d_note(doc, method):
    if doc.supplier_delivery_note:
        posting_date = nowdate()
        posting_time = nowtime()
        _purchase_invoice = frappe.db.get_value('Purchase Invoice', {'custom_linked_sales_invoice': doc.custom_linked_sales_invoice}, ['name'], as_dict=1) 
        if _purchase_invoice:
            purchase_invoice = frappe.get_doc("Purchase Invoice", _purchase_invoice.name)
            
            transport_amount = frappe.get_all("Transport Setting", fields=["transport_amount"], limit=1)
            
            d_items = []
            d_p_items = []
            c_c_note = []
            
            
            for itm in doc.items:
                if itm.custom_shortage and itm.custom_shortage > 0:
                    d_items.append(frappe._dict({
                        'item_code': itm.item_code,
                        'item_name': itm.item_name,
                        'description': f"{itm.description}",
                        'received_qty': -abs(itm.custom_shortage),
                        'conversion_factor': 1,
                        'qty': -abs(itm.custom_shortage),
                        "rate": itm.rate,
                        'uom': itm.uom,
                        'stock_qty': -abs(itm.custom_shortage)
                    }))
                    
                    c_c_note.append(frappe._dict({
                        'item_code': itm.item_code,
                        'item_name': itm.item_name,
                        'description': f"{itm.description}",
                        'conversion_factor': 1,
                        'qty': -abs(itm.custom_shortage),
                        "rate": itm.rate,
                        'uom': itm.uom,
                    }))
                    
                    if itm.custom_chargeable_loss > 0:
                        qty = (itm.custom_chargeable_loss / 1000)
                        d_p_items.append(frappe._dict({
                            'item_code': "TRANSPORT SERVICE",
                            'item_name': "TRANSPORT SERVICE",
                            'description': f"{itm.description}",
                            'received_qty': -abs(qty),
                            'conversion_factor': 1,
                            'qty': -abs(qty),
                            "rate": transport_amount[0].transport_amount,
                            'uom': "Cubic Meter",
                            'stock_qty': -abs(qty)
                        }))
                     
            _s_p_invoice = frappe.db.get_value('Purchase Invoice', {'custom_delivery_note_number': doc.supplier_delivery_note}, ['name'], as_dict=1) 
            if _s_p_invoice:
                s_p_invoice = frappe.get_doc("Purchase Invoice", _s_p_invoice.name)
                if s_p_invoice.docstatus == 1:
                    if len(d_p_items) > 0:
                        s_d_invoice = frappe.new_doc("Purchase Invoice")
                        s_d_invoice.naming_series = "ACC-PINV-.YYYY.-"
                        s_d_invoice.bill_no = s_p_invoice.bill_no
                        s_d_invoice.bill_date = s_p_invoice.bill_date
                        s_d_invoice.update_outstanding_for_self = 0
                        s_d_invoice.is_return = 1
                        s_d_invoice.return_against = s_p_invoice.name
                        s_d_invoice.update_billed_amount_in_purchase_receipt = 1
                        s_d_invoice.supplier = s_p_invoice.supplier
                        s_d_invoice.posting_date = posting_date
                        s_d_invoice.posting_time = posting_time
                        s_d_invoice.set_posting_time = 1
                        s_d_invoice.company = s_p_invoice.company
                            
                        s_d_invoice.set("items", d_p_items)
                        s_d_invoice.flags.ignore_permissions = True
                        s_d_invoice.set_missing_values()
                        s_d_invoice.save(ignore_permissions=True)
                    
                   
            if len(d_items) > 0: 
                p_invoice = frappe.new_doc("Purchase Invoice")
                p_invoice.naming_series = "ACC-PINV-.YYYY.-"
                p_invoice.bill_no = purchase_invoice.bill_no
                p_invoice.bill_date = purchase_invoice.bill_date
                p_invoice.update_outstanding_for_self = 0
                p_invoice.is_return = 1
                p_invoice.return_against = purchase_invoice.name
                p_invoice.update_billed_amount_in_purchase_receipt = 1
                p_invoice.supplier = purchase_invoice.supplier
                p_invoice.posting_date = posting_date
                p_invoice.posting_time = posting_time
                p_invoice.set_posting_time = 1
                p_invoice.company = purchase_invoice.company
                    
                p_invoice.set("items", d_items)
                p_invoice.flags.ignore_permissions = True
                p_invoice.set_missing_values()
                p_invoice.save(ignore_permissions=True)
                
                frappe.flags.ignore_account_permission = True
                p_invoice.submit()
                
            if len(c_c_note) > 0:
                sales_invoice = frappe.get_doc("Sales Invoice", doc.custom_linked_sales_invoice)
                c_credit_note = frappe.new_doc("Sales Invoice")
                c_credit_note.naming_series = "ACC-SINV-.YYYY.-"
                c_credit_note.posting_date = posting_date
                c_credit_note.posting_time = posting_time
                c_credit_note.customer = sales_invoice.customer
                c_credit_note.company = sales_invoice.company
                c_credit_note.is_return = 1
                c_credit_note.return_against = sales_invoice.name
                c_credit_note.update_outstanding_for_self = 0
                c_credit_note.update_billed_amount_in_delivery_note = 1
                
                c_credit_note.set("items", c_c_note)
                c_credit_note.flags.ignore_permissions = True
                c_credit_note.set_missing_values()
                c_credit_note.save(ignore_permissions=True)
            
                
        frappe.db.commit() 
    
        

def on_submit(doc, method):
    if doc.status == "To Bill":
        pr = frappe.get_doc("Purchase Receipt", doc.name)
        pr.update_status("Closed")
        frappe.db.commit() 
    
@frappe.whitelist()
def generate_delivery_note(**args):
    try:
        args = frappe._dict(args)
        posting_time = nowtime()
        print(args.name)
        instruction = frappe.get_doc("Release Instruction", args.name)
        sales_order = None
        if instruction.linked_sales_order:
            sales_order = frappe.get_doc("Sales Order", instruction.linked_sales_order)
        for itm in instruction.items:
            delivery_note = frappe.new_doc("Delivery Note")
            delivery_note.custom_release_instruction = instruction.name
            delivery_note.naming_series = "MAT-DN-.YYYY.-"
            delivery_note.posting_date = itm.release_date if itm.release_date else instruction.date
            delivery_note.posting_time = posting_time
            delivery_note.company = instruction.company
            delivery_note.customer = instruction.customer
            delivery_note.transporter = itm.transporter if itm.transporter else instruction.transporter
            delivery_note.driver = itm.driver
            delivery_note.custom_vehicle = itm.truck_reg
            delivery_note.custom_trailer_no = itm.trailer_reg
            delivery_note.set_warehouse = instruction.loadingsource_depot
            delivery_note.po_no = sales_order.po_no if sales_order else None
            delivery_note.po_date = sales_order.po_date if sales_order else None
            
            d_items = []
            d_items.append(frappe._dict({
                'item_code': instruction.product,
                'item_name': instruction.product,
                'description': f"{instruction.product}",
                'conversion_factor': 1,
                'qty': itm.capacity,
                'custom_loaded_qty': itm.loaded_capacity20,
                "rate": itm.selling_price if itm.selling_price else instruction.selling_price,
                'uom': "Litre",
                'stock_uom': "Litre",
                'use_serial_batch_fields': 1,
                'batch_no': itm.batch_number if itm.batch_number else instruction.batch_number
            }))
            delivery_note.set("items", d_items)
            delivery_note.flags.ignore_permissions = True
            frappe.flags.ignore_account_permission = True
            delivery_note.set_missing_values()
            delivery_note.save(ignore_permissions=True)
            delivery_note.submit()
            
            sales_invoice = make_sales_invoice(delivery_note.name)
            sales_invoice.custom_transporter = itm.transporter if itm.transporter else instruction.transporter
            sales_invoice.custom_driver = itm.driver
            sales_invoice.custom_vehicle = itm.truck_reg
            sales_invoice.custom_trailer_no = itm.trailer_reg
            sales_invoice.custom_release_instructions = instruction.name
            sales_invoice.flags.ignore_permissions = True
            frappe.flags.ignore_account_permission = True
            sales_invoice.set_missing_values()
            sales_invoice.save(ignore_permissions=True)
            sales_invoice.submit()
            
            dn = frappe.get_doc("Delivery Note", delivery_note.name)
            dn.update_status("Closed")


        frappe.db.commit() 
        return True
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), str(e))
        return f"Failed. {str(e)}"
    
def get_returned_qty_map(delivery_note):
	"""returns a map: {so_detail: returned_qty}"""
	returned_qty_map = frappe._dict(
		frappe.db.sql(
			"""select dn_item.dn_detail, abs(dn_item.qty) as qty
		from `tabDelivery Note Item` dn_item, `tabDelivery Note` dn
		where dn.name = dn_item.parent
			and dn.docstatus = 1
			and dn.is_return = 1
			and dn.return_against = %s
	""",
			delivery_note,
		)
	)

	return returned_qty_map

def get_invoiced_qty_map(delivery_note):
	"""returns a map: {dn_detail: invoiced_qty}"""
	invoiced_qty_map = {}

	for dn_detail, qty in frappe.db.sql(
		"""select dn_detail, qty from `tabSales Invoice Item`
		where delivery_note=%s and docstatus=1""",
		delivery_note,
	):
		if not invoiced_qty_map.get(dn_detail):
			invoiced_qty_map[dn_detail] = 0
		invoiced_qty_map[dn_detail] += qty

	return invoiced_qty_map

@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None, args=None):
	doc = frappe.get_doc("Delivery Note", source_name)

	to_make_invoice_qty_map = {}
	returned_qty_map = get_returned_qty_map(source_name)
	invoiced_qty_map = get_invoiced_qty_map(source_name)

	def set_missing_values(source, target):
		target.run_method("set_missing_values")
		target.run_method("set_po_nos")

		if len(target.get("items")) == 0:
			frappe.throw(_("All these items have already been Invoiced/Returned"))

		if args and args.get("merge_taxes"):
			merge_taxes(source.get("taxes") or [], target)

		target.run_method("calculate_taxes_and_totals")

		# set company address
		if source.company_address:
			target.update({"company_address": source.company_address})
		else:
			# set company address
			target.update(get_company_address(target.company))

		if target.company_address:
			target.update(get_fetch_values("Sales Invoice", "company_address", target.company_address))

	def update_item(source_doc, target_doc, source_parent):
		target_doc.qty = to_make_invoice_qty_map[source_doc.name]

		if source_doc.serial_no and source_parent.per_billed > 0 and not source_parent.is_return:
			target_doc.serial_no = get_delivery_note_serial_no(
				source_doc.item_code, target_doc.qty, source_parent.name
			)

	def get_pending_qty(item_row):
		pending_qty = item_row.custom_loaded_qty - invoiced_qty_map.get(item_row.name, 0)

		returned_qty = 0
		if returned_qty_map.get(item_row.name, 0) > 0:
			returned_qty = flt(returned_qty_map.get(item_row.name, 0))
			returned_qty_map[item_row.name] -= pending_qty

		if returned_qty:
			if returned_qty >= pending_qty:
				pending_qty = 0
				returned_qty -= pending_qty
			else:
				pending_qty -= returned_qty
				returned_qty = 0

		to_make_invoice_qty_map[item_row.name] = pending_qty

		return pending_qty

	doc = get_mapped_doc(
		"Delivery Note",
		source_name,
		{
			"Delivery Note": {
				"doctype": "Sales Invoice",
				"field_map": {"is_return": "is_return"},
				"validation": {"docstatus": ["=", 1]},
			},
			"Delivery Note Item": {
				"doctype": "Sales Invoice Item",
				"field_map": {
					"name": "dn_detail",
					"parent": "delivery_note",
					"so_detail": "so_detail",
					"against_sales_order": "sales_order",
					"serial_no": "serial_no",
					"cost_center": "cost_center",
				},
				"postprocess": update_item,
				"filter": lambda d: get_pending_qty(d) <= 0
				if not doc.get("is_return")
				else get_pending_qty(d) > 0,
			},
			"Sales Taxes and Charges": {
				"doctype": "Sales Taxes and Charges",
				"add_if_empty": True,
				"ignore": args.get("merge_taxes") if args else 0,
			},
			"Sales Team": {
				"doctype": "Sales Team",
				"field_map": {"incentives": "incentives"},
				"add_if_empty": True,
			},
		},
		target_doc,
		set_missing_values,
	)

	automatically_fetch_payment_terms = cint(
		frappe.db.get_single_value("Accounts Settings", "automatically_fetch_payment_terms")
	)
	if automatically_fetch_payment_terms:
		doc.set_payment_schedule()

	return doc


def get_delivery_note_serial_no(item_code, qty, delivery_note):
	serial_nos = ""
	dn_serial_nos = frappe.db.sql_list(
		f""" select name from `tabSerial No`
		where item_code = %(item_code)s and delivery_document_no = %(delivery_note)s
		and sales_invoice is null limit {cint(qty)}""",
		{"item_code": item_code, "delivery_note": delivery_note},
	)

	if dn_serial_nos and len(dn_serial_nos) > 0:
		serial_nos = "\n".join(dn_serial_nos)

	return serial_nos

