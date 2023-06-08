output "resource_group_name" {
  value = azurerm_resource_group.e2eanalyticsrg.name
}

output "synapse_ws_endpoints" {
  value = azurerm_synapse_workspace.e2esynapse.connectivity_endpoints
}
