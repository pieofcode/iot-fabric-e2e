variable "resource_group_name_prefix" {
  default     = "rg"
  description = "Prefix of the resource group name that's combined with a random ID so name is unique in your Azure subscription."
}

variable "resource_group_location" {
  default     = "eastus2"
  description = "Location of the resource group."
}

variable "subscription_id" {
  default     = ""
  description = "Azure subscription Id"
}

variable "tenant_id" {
  default     = ""
  description = "Azure tenant Id"
}

variable "client_id" {
  default     = ""
  description = "Service Principal client Id"
}

variable "principal_id" {
  default     = "89d138d3-dfee-400b-9bc1-36347bf60c9a"
  description = "Service Principal client Id"
}

variable "client_secret" {
  default     = ""
  description = "Service Principal client secret"
}
