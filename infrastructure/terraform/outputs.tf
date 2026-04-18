output "aks_cluster_name"    { value = azurerm_kubernetes_cluster.main.name }
output "openai_endpoint"     { value = azurerm_cognitive_account.openai.endpoint }
output "search_endpoint"     { value = "https://${azurerm_search_service.main.name}.search.windows.net" }
output "redis_hostname"      { value = azurerm_redis_cache.main.hostname }
output "cosmos_endpoint"     { value = azurerm_cosmosdb_account.main.endpoint }
output "storage_account"     { value = azurerm_storage_account.main.name }
output "key_vault_uri"       { value = azurerm_key_vault.main.vault_uri }
output "app_insights_key"    { value = azurerm_application_insights.main.instrumentation_key; sensitive = true }
output "resource_group_name" { value = azurerm_resource_group.main.name }
