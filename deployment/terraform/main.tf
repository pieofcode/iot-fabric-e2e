data "azurerm_client_config" "current" {}

resource "random_string" "random_suffix" {
  length  = 4
  special = false
  upper   = false
}

resource "azurerm_resource_group" "e2eanalyticsrg" {
  name     = "e2e-analytics-rg-${random_string.random_suffix.result}"
  location = var.resource_group_location
}

resource "azurerm_storage_account" "e2estorageaccount" {
  name                     = "e2estorageaccount${random_string.random_suffix.result}"
  location                 = var.resource_group_location
  resource_group_name      = azurerm_resource_group.e2eanalyticsrg.name
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "setup" {
  name                  = "setup-files"
  storage_account_name  = azurerm_storage_account.e2estorageaccount.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "telemetry" {
  name                  = "telemetry-raw"
  storage_account_name  = azurerm_storage_account.e2estorageaccount.name
  container_access_type = "private"
}


# Create an Azure IoT Hub
resource "azurerm_iothub" "e2eiothub" {
  name = "e2e-iothub-${random_string.random_suffix.result}"

  # "azurerm_resource_group.b59" is an Azure Resource Group
  # defined elsewhere in the Terraform project
  resource_group_name = azurerm_resource_group.e2eanalyticsrg.name
  location            = var.resource_group_location


  # Define the Pricing Tier (SKU & Capacity)
  sku {
    name     = "S1"
    capacity = 1
  }

  endpoint {
    type                       = "AzureIotHub.StorageContainer"
    connection_string          = azurerm_storage_account.e2estorageaccount.primary_blob_connection_string
    name                       = "export"
    batch_frequency_in_seconds = 60
    max_chunk_size_in_bytes    = 10485760
    container_name             = azurerm_storage_container.telemetry.name
    encoding                   = "Avro"
    file_name_format           = "{iothub}/{partition}/{YYYY}/{MM}/{DD}/{HH}/{mm}"
  }

  route {
    name           = "export"
    source         = "DeviceMessages"
    condition      = "true"
    endpoint_names = ["export"]
    enabled        = true
  }

  cloud_to_device {
    max_delivery_count = 30
    default_ttl        = "PT1H"
    feedback {
      time_to_live       = "PT1H10M"
      max_delivery_count = 15
      lock_duration      = "PT30S"
    }
  }
}

resource "azurerm_iothub_consumer_group" "consumer_group" {
  name                   = "adxconsumergroup"
  iothub_name            = azurerm_iothub.e2eiothub.name
  eventhub_endpoint_name = "events"
  resource_group_name    = azurerm_resource_group.e2eanalyticsrg.name
}

# Create an IoT Hub Access Policy
data "azurerm_iothub_shared_access_policy" "e2eiothubowner" {
  name                = "iothubowner"
  resource_group_name = azurerm_resource_group.e2eanalyticsrg.name
  iothub_name         = azurerm_iothub.e2eiothub.name
}

# Create a Device Provisioning Service
resource "azurerm_iothub_dps" "iote2edps" {
  name                = "iote2edps-${random_string.random_suffix.result}"
  resource_group_name = azurerm_resource_group.e2eanalyticsrg.name
  location            = var.resource_group_location

  sku {
    name     = "S1"
    capacity = 1
  }
  linked_hub {
    connection_string = data.azurerm_iothub_shared_access_policy.e2eiothubowner.primary_connection_string
    location          = var.resource_group_location
  }
}

resource "azurerm_storage_blob" "script" {
  name                   = "setup.txt"
  storage_account_name   = azurerm_storage_account.e2estorageaccount.name
  storage_container_name = azurerm_storage_container.setup.name
  type                   = "Block"
  source                 = "./data/setup.txt"
}

data "azurerm_storage_account_blob_container_sas" "setup_sas" {
  connection_string = azurerm_storage_account.e2estorageaccount.primary_connection_string
  container_name    = azurerm_storage_container.setup.name
  https_only        = true

  start  = "2022-10-01"
  expiry = "2023-12-31"

  permissions {
    read   = true
    add    = false
    create = false
    write  = true
    delete = false
    list   = true
  }
}

resource "azurerm_storage_data_lake_gen2_filesystem" "e2eadls" {
  name               = "e2eadls-${random_string.random_suffix.result}"
  storage_account_id = azurerm_storage_account.e2estorageaccount.id
}


resource "azurerm_synapse_workspace" "e2esynapse" {
  name                                 = "e2esynapse-${random_string.random_suffix.result}"
  resource_group_name                  = azurerm_resource_group.e2eanalyticsrg.name
  location                             = var.resource_group_location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.e2eadls.id
  sql_administrator_login              = "sqladminuser"
  sql_administrator_login_password     = "H@Sh1CoR3!"

  identity {
    type = "SystemAssigned"
  }
}
resource "azurerm_synapse_firewall_rule" "rule" {
  name                 = "AllowAll"
  synapse_workspace_id = azurerm_synapse_workspace.e2esynapse.id
  start_ip_address     = "0.0.0.0"
  end_ip_address       = "255.255.255.255"
}

resource "azurerm_synapse_role_assignment" "synapserole" {
  synapse_workspace_id = azurerm_synapse_workspace.e2esynapse.id
  role_name            = "Synapse Administrator"
  principal_id         = var.principal_id

  depends_on = [azurerm_synapse_firewall_rule.rule]
}

resource "azurerm_synapse_spark_pool" "devsparkpool" {
  name                 = "sparkpool${random_string.random_suffix.result}"
  synapse_workspace_id = azurerm_synapse_workspace.e2esynapse.id
  node_size_family     = "MemoryOptimized"
  node_size            = "Small"
  node_count           = 3
}

resource "azapi_resource" "synapseadxcluster" {
  type      = "Microsoft.Synapse/workspaces/kustoPools@2021-06-01-preview"
  name      = "adxcluster${random_string.random_suffix.result}"
  location  = var.resource_group_location
  parent_id = azurerm_synapse_workspace.e2esynapse.id
  tags = {
    tagName1 = "tagValue1"
    tagName2 = "tagValue2"
  }
  body = jsonencode({
    properties = {
      enablePurge           = true
      enableStreamingIngest = true
      optimizedAutoscale = {
        isEnabled = false
        maximum   = 3
        minimum   = 1
        version   = 1
      }
      workspaceUID = "fbc0e649-28d5-4bc9-989c-93e9519dc127"
    }
    sku = {
      capacity = 2
      name     = "Compute optimized"
      size     = "Extra small"
    }
  })
}

resource "azapi_resource" "adxdatabase" {
  type      = "Microsoft.Synapse/workspaces/kustoPools/databases@2021-06-01-preview"
  name      = "Manufacturing"
  location  = var.resource_group_location
  parent_id = azapi_resource.synapseadxcluster.id
  // For remaining properties, see workspaces/kustoPools/databases objects
  body = jsonencode({
    kind = "ReadWrite"
    name = "Manufacturing"
    properties = {
      hotCachePeriod   = "P1Y0M0D"
      softDeletePeriod = "P3Y0M0D"
    }
  })
}

resource "azapi_resource" "adxdbprincipal" {
  type      = "Microsoft.Synapse/workspaces/kustoPools/principalAssignments@2021-06-01-preview"
  name      = "adxdbprincipal${random_string.random_suffix.result}"
  parent_id = azapi_resource.synapseadxcluster.id
  body = jsonencode({
    properties = {
      principalId   = var.principal_id
      principalType = "User"
      role          = "AllDatabasesAdmin"
      tenantId      = var.tenant_id
    }
  })
}

# resource "azurerm_kusto_script" "init" {
#   name                               = "init"
#   database_id                        = azapi_resource.adxdatabase.id
#   url                                = azurerm_storage_blob.script.id
#   sas_token                          = data.azurerm_storage_account_blob_container_sas.setup_sas.sas
#   continue_on_errors_enabled         = true
#   force_an_update_when_value_changed = "first"
# }

resource "azapi_resource" "adxiothubdataconnection" {
  type      = "Microsoft.Synapse/workspaces/kustoPools/databases/dataConnections@2021-06-01-preview"
  name      = "iothubdataconnection"
  location  = var.resource_group_location
  parent_id = azapi_resource.adxdatabase.id
  // For remaining properties, see workspaces/kustoPools/databases/dataConnections objects
  body = jsonencode({
    kind = "IotHub"
    name = "iothubdataconnection"
    properties = {
      consumerGroup = azurerm_iothub_consumer_group.consumer_group.name
      dataFormat    = "JSON"
      eventSystemProperties = [
        "message-id",
        "iothub-enqueuedtime",
        "iothub-connection-device-id",
        "iothub-creation-time-utc"
      ]
      iotHubResourceId       = azurerm_iothub.e2eiothub.id
      mappingRuleName        = "landingMapping"
      sharedAccessPolicyName = data.azurerm_iothub_shared_access_policy.e2eiothubowner.name
      tableName              = "Landing"
    }
  })
}

# resource "azurerm_kusto_cluster" "e2eadxcluster" {
#   name                = "e2eadxcluster"
#   location            = var.resource_group_location
#   resource_group_name = azurerm_resource_group.e2eanalyticsrg.name

#   sku {
#     name     = "Standard_D13_v2"
#     capacity = 2
#   }

#   tags = {
#     Environment = "Production"
#   }
# }

# resource "azurerm_kusto_cluster_principal_assignment" "example" {
#   name                = "KustoPrincipalAssignment"
#   resource_group_name = azurerm_resource_group.e2eanalyticsrg.name
#   cluster_name        = azurerm_kusto_cluster.e2eadxcluster.name

#   tenant_id      = data.azurerm_client_config.current.tenant_id
#   principal_id   = data.azurerm_client_config.current.client_id
#   principal_type = "App"
#   role           = "AllDatabasesAdmin"
# }
