variable "project_name"        { default = "oc-copilot" }
variable "project_name_short"  { default = "occopilot" }
variable "environment"         { default = "production" }
variable "location"            { default = "East US 2" }
variable "resource_group_name" { default = "rg-oc-copilot-prod" }
variable "sql_admin_username"  { sensitive = true; default = "oc-admin" }
variable "sql_admin_password"  { sensitive = true }
