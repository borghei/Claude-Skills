// Deliberately flawed Bicep for azure_architecture_validator.py (expect BC001, BC002, BC003, BC005, BC006).
param location string = resourceGroup().location

resource sa 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'stlegacydemo001'
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: true
    allowSharedKeyAccess: true
    supportsHttpsTrafficOnly: false
    minimumTlsVersion: 'TLS1_0'
    publicNetworkAccess: 'Enabled'
  }
}
