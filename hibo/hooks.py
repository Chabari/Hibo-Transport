app_name = "hibo"
app_title = "Hibo Customizations"
app_publisher = "George Mukundi"
app_description = "Hibo Customizations"
app_email = "georgemukundi5@gmail.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/hibo/css/hibo.css"
# app_include_js = "/assets/hibo/js/hibo.js"

# include js, css files in header of web template
# web_include_css = "/assets/hibo/css/hibo.css"
# web_include_js = "/assets/hibo/js/hibo.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hibo/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "hibo/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "hibo.utils.jinja_methods",
# 	"filters": "hibo.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "hibo.install.before_install"
# after_install = "hibo.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "hibo.uninstall.before_uninstall"
# after_uninstall = "hibo.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "hibo.utils.before_app_install"
# after_app_install = "hibo.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "hibo.utils.before_app_uninstall"
# after_app_uninstall = "hibo.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hibo.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {

    "Purchase Order": {
        "before_submit": "hibo.api.create_order",
    },
    "Delivery Note": {
        "before_submit": "hibo.api.create_s_p_invoice",
    },
    "Sales Invoice": {
        "before_submit": "hibo.api.create_c_i_invoice",
    },
    "Purchase Receipt": {
        "before_submit": "hibo.api.create_d_note",
    }
}


fixtures = [

    {
        "doctype": "Workflow State"
    },
    {
        "doctype": "Workflow Transition"
    },
    {
        "doctype": "Workflow"
    },
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                (
                    "Purchase Order-custom_target_company",
                    "Vehicle-custom_trailer_number",
                    "Delivery Note-custom_vehicle",
                    "Delivery Note-custom_trailer_no",
                    "Purchase Invoice-custom_delivery_note_number",
                    "Purchase Invoice-custom_linked_sales_invoice",
                    "Purchase Receipt-custom_linked_sales_invoice",
                    "Purchase Receipt Item-custom_offloaded_qty20",
                    "Purchase Receipt Item-custom_loaded_quantity",
                    "Purchase Receipt Item-custom_shortage",
                    "Purchase Receipt Item-custom_allowable_loss",
                    "Purchase Receipt Item-custom_chargeable_loss",
                    "Release Instruction-workflow_state",
                    "Delivery Note-custom_release_instruction",
                    "Delivery Note Item-custom_loaded_qty",
                    "Driver-custom_passport_number",
                ),
            ]
        ],
    },
    
]


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"hibo.tasks.all"
# 	],
# 	"daily": [
# 		"hibo.tasks.daily"
# 	],
# 	"hourly": [
# 		"hibo.tasks.hourly"
# 	],
# 	"weekly": [
# 		"hibo.tasks.weekly"
# 	],
# 	"monthly": [
# 		"hibo.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "hibo.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "hibo.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "hibo.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["hibo.utils.before_request"]
# after_request = ["hibo.utils.after_request"]

# Job Events
# ----------
# before_job = ["hibo.utils.before_job"]
# after_job = ["hibo.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"hibo.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

