metadata name = 'Azure Container Registry'
metadata description = 'This module deploys an Azure Container Registry with managed identity authentication support.'

@description('Required. The name of the Container Registry.')
param name string

@description('Optional. Location for the Container Registry.')
param location string = resourceGroup().location

@description('Optional. The tags to apply to the Container Registry.')
param tags object = {}

@description('Optional. The SKU name of the Container Registry.')
@allowed(['Basic', 'Standard', 'Premium'])
param sku string = 'Standard'

@description('Optional. Enable admin user for the Container Registry.')
param adminUserEnabled bool = false

@description('Optional. Public network access setting.')
@allowed(['Enabled', 'Disabled'])
param publicNetworkAccess string = 'Enabled'

@description('Optional. Enable zone redundancy for the Container Registry.')
param zoneRedundancy bool = false

@description('Optional. Enable data endpoint for the Container Registry.')
param dataEndpointEnabled bool = false

@description('Optional. Network rule bypass options.')
@allowed(['None', 'AzureServices'])
param networkRuleBypassOptions string = 'AzureServices'

@description('Optional. Role assignments to create for the Container Registry.')
param roleAssignments array = []

@description('Optional. Diagnostic settings for the Container Registry.')
param diagnosticSettings array = []

// Variables
var builtInRoleNames = {
  AcrDelete: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'c2f4ef07-c644-48eb-af81-4b1b4947fb11')
  AcrImageSigner: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '6cef56e8-d556-48e5-a04f-b8e64114680f')
  AcrPull: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  AcrPush: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8311e382-0749-4cb8-b61a-304f252e45ec')
  AcrQuarantineReader: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'cdda3590-29a3-44f6-95f2-9f980659eb04')
  AcrQuarantineWriter: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'c8d4ff99-41c3-41a8-9f60-21dfdad59608')
  Contributor: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b24988ac-6180-42a0-ab88-20f7382dd24c')
  Owner: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8e3af657-a8ff-443c-a75c-2fe8c4bcb635')
  Reader: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'acdd72a7-3385-48ef-bd42-f606fba81ae7')
  'Role Based Access Control Administrator (Preview)': subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'f58310d9-a9f6-439a-9e8d-f62e7b41a168')
  'User Access Administrator': subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '18d7d88d-d35e-4fb5-a5c3-7773c20a72d9')
}

// Resources
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: sku
  }
  properties: {
    adminUserEnabled: adminUserEnabled
    publicNetworkAccess: publicNetworkAccess
    zoneRedundancy: zoneRedundancy ? 'Enabled' : 'Disabled'
    dataEndpointEnabled: dataEndpointEnabled
    networkRuleBypassOptions: networkRuleBypassOptions
  }
}

resource containerRegistry_diagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = [for (diagnosticSetting, index) in (diagnosticSettings ?? []): {
  name: diagnosticSetting.?name ?? '${name}-diagnosticSettings'
  properties: {
    storageAccountId: diagnosticSetting.?storageAccountResourceId
    workspaceId: diagnosticSetting.?workspaceResourceId
    eventHubAuthorizationRuleId: diagnosticSetting.?eventHubAuthorizationRuleResourceId
    eventHubName: diagnosticSetting.?eventHubName
    metrics: [for group in (diagnosticSetting.?metricCategories ?? [ { category: 'AllMetrics' } ]): {
      category: group.category
      enabled: group.?enabled ?? true
      timeGrain: null
    }]
    logs: [for group in (diagnosticSetting.?logCategories ?? []): {
      categoryGroup: group.?categoryGroup
      category: group.?category
      enabled: group.?enabled ?? true
    }]
    marketplacePartnerId: diagnosticSetting.?marketplacePartnerResourceId
    logAnalyticsDestinationType: diagnosticSetting.?logAnalyticsDestinationType
  }
  scope: containerRegistry
}]

resource containerRegistry_roleAssignments 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for (roleAssignment, index) in (roleAssignments ?? []): {
  name: guid(containerRegistry.id, roleAssignment.principalId, roleAssignment.roleDefinitionIdOrName)
  properties: {
    roleDefinitionId: contains(builtInRoleNames, roleAssignment.roleDefinitionIdOrName) ? builtInRoleNames[roleAssignment.roleDefinitionIdOrName] : contains(roleAssignment.roleDefinitionIdOrName, '/providers/Microsoft.Authorization/roleDefinitions/') ? roleAssignment.roleDefinitionIdOrName : subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleAssignment.roleDefinitionIdOrName)
    principalId: roleAssignment.principalId
    description: roleAssignment.?description
    principalType: roleAssignment.?principalType
    condition: roleAssignment.?condition
    conditionVersion: !empty(roleAssignment.?condition) ? (roleAssignment.?conditionVersion ?? '2.0') : null
    delegatedManagedIdentityResourceId: roleAssignment.?delegatedManagedIdentityResourceId
  }
  scope: containerRegistry
}]

// Outputs
@description('The resource ID of the Container Registry.')
output resourceId string = containerRegistry.id

@description('The name of the Container Registry.')
output name string = containerRegistry.name

@description('The location the Container Registry was deployed into.')
output location string = containerRegistry.location

@description('The resource group the Container Registry was deployed into.')
output resourceGroupName string = resourceGroup().name

@description('The login server for the Container Registry.')
output loginServer string = containerRegistry.properties.loginServer

@description('The principal ID of the system assigned identity.')
output systemAssignedMIPrincipalId string = containerRegistry.?identity.?principalId ?? ''
