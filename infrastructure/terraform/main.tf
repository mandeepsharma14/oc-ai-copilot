###############################################################################
# OC AI Copilot — Azure Infrastructure (Terraform)
###############################################################################
terraform {
  required_version = ">= 1.7.0"
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 3.100" }
  }
  backend "azurerm" {
    resource_group_name  = "rg-oc-copilot-tfstate"
    storage_account_name = "stoccopilottfstate"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
  }
}

provider "azurerm" {
  features {
    resource_group { prevent_deletion_if_contains_resources = true }
    key_vault      { purge_soft_delete_on_destroy = false }
  }
}

locals {
  tags = {
    project     = var.project_name
    environment = var.environment
    owner       = "andy.sharma@owenscorning.com"
    managed_by  = "terraform"
  }
}

data "azurerm_client_config" "current" {}

###############################################################################
# Resource Group
###############################################################################
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = local.tags
}

###############################################################################
# Azure OpenAI
###############################################################################
resource "azurerm_cognitive_account" "openai" {
  name                = "oai-${var.project_name}-${var.environment}"
  location            = "East US"
  resource_group_name = azurerm_resource_group.main.name
  kind                = "OpenAI"
  sku_name            = "S0"
  tags                = local.tags
}

resource "azurerm_cognitive_deployment" "gpt4o" {
  name                 = "gpt-4o"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  model { format = "OpenAI"; name = "gpt-4o";      version = "2024-05-13" }
  scale { type = "GlobalStandard"; capacity = 40 }
}

resource "azurerm_cognitive_deployment" "gpt4o_mini" {
  name                 = "gpt-4o-mini"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  model { format = "OpenAI"; name = "gpt-4o-mini"; version = "2024-07-18" }
  scale { type = "GlobalStandard"; capacity = 120 }
}

resource "azurerm_cognitive_deployment" "embeddings" {
  name                 = "text-embedding-3-large"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  model { format = "OpenAI"; name = "text-embedding-3-large"; version = "1" }
  scale { type = "Standard"; capacity = 30 }
}

###############################################################################
# Azure AI Search
###############################################################################
resource "azurerm_search_service" "main" {
  name                = "srch-${var.project_name}-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "standard2"
  replica_count       = var.environment == "production" ? 3 : 1
  partition_count     = var.environment == "production" ? 2 : 1
  tags                = local.tags
}

###############################################################################
# AKS
###############################################################################
resource "azurerm_kubernetes_cluster" "main" {
  name                = "aks-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "${var.project_name}-${var.environment}"
  kubernetes_version  = "1.29"
  tags                = local.tags

  default_node_pool {
    name                = "system"
    node_count          = 3
    vm_size             = "Standard_D4s_v3"
    enable_auto_scaling = true
    min_count           = 2
    max_count           = 10
    os_disk_size_gb     = 100
    type                = "VirtualMachineScaleSets"
    zones               = ["1", "2", "3"]
  }

  identity { type = "SystemAssigned" }

  network_profile {
    network_plugin    = "azure"
    load_balancer_sku = "standard"
  }

  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  }
}

resource "azurerm_kubernetes_cluster_node_pool" "app" {
  name                  = "apppool"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = "Standard_D8s_v3"
  node_count            = 3
  enable_auto_scaling   = true
  min_count             = 3
  max_count             = var.environment == "production" ? 200 : 20
  mode                  = "User"
  zones                 = ["1", "2", "3"]
  node_labels           = { "workload" = "app" }
}

###############################################################################
# Redis, Cosmos DB, SQL, Storage, Key Vault, Monitoring
###############################################################################
resource "azurerm_redis_cache" "main" {
  name                = "redis-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = var.environment == "production" ? 2 : 1
  family              = "C"
  sku_name            = var.environment == "production" ? "Standard" : "Basic"
  minimum_tls_version = "1.2"
  tags                = local.tags
  redis_configuration { maxmemory_policy = "allkeys-lru" }
}

resource "azurerm_cosmosdb_account" "main" {
  name                = "cosmos-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
  tags                = local.tags
  consistency_policy  { consistency_level = "Session" }
  geo_location        { location = azurerm_resource_group.main.location; failover_priority = 0 }
  capabilities        { name = "EnableServerless" }
}

resource "azurerm_storage_account" "main" {
  name                     = "st${var.project_name_short}${var.environment}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = var.environment == "production" ? "GRS" : "LRS"
  min_tls_version          = "TLS1_2"
  tags                     = local.tags
  blob_properties { versioning_enabled = true }
}

resource "azurerm_storage_container" "internal_docs" {
  name                  = "internal-docs"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "external_docs" {
  name                  = "external-docs"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

resource "azurerm_key_vault" "main" {
  name                       = "kv-${var.project_name}-${var.environment}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  purge_protection_enabled   = var.environment == "production"
  soft_delete_retention_days = 90
  tags                       = local.tags
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = "log-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = var.environment == "production" ? 90 : 30
  tags                = local.tags
}

resource "azurerm_application_insights" "main" {
  name                = "appi-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  tags                = local.tags
}
