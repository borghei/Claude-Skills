# Secrets Management Guide

## Core Principles

1. **Never hardcode secrets** in source code, configs, or documentation
2. **Encrypt at rest and in transit** - all secrets must be encrypted
3. **Least privilege access** - grant minimum necessary access
4. **Rotate regularly** - secrets have expiration dates
5. **Audit everything** - log all access and changes

## Secret Classification

| Level | Examples | Rotation Frequency | Access Control |
|-------|---------|-------------------|----------------|
| Critical | DB root creds, master encryption keys | 30 days | Named individuals only |
| High | Service tokens, OAuth secrets, TLS certs | 60-90 days | Team-level access |
| Medium | Third-party API keys, webhook secrets | 90-180 days | Service-level access |
| Low | Public API keys, non-sensitive config | 365 days | Broad access OK |

## HashiCorp Vault Architecture

### Secrets Engines

- **KV (Key-Value)**: General-purpose secret storage (v2 recommended for versioning)
- **Database**: Dynamic database credential generation
- **Transit**: Encryption as a service (encrypt/decrypt without exposing keys)
- **PKI**: X.509 certificate management
- **AWS/GCP/Azure**: Cloud provider dynamic credentials
- **SSH**: SSH certificate signing

### Auth Methods

- **AppRole**: Machine-to-machine authentication
- **Kubernetes**: Pod-based authentication
- **OIDC/JWT**: SSO integration
- **Token**: Direct token authentication
- **Userpass**: Username/password (dev/testing only)

### Access Policies

```hcl
# Example: Read-only access to production KV
path "secret/data/production/*" {
  capabilities = ["read", "list"]
}

# Example: Full access to team secrets
path "secret/data/team/engineering/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
```

## Rotation Best Practices

### Automated Rotation
- Use Vault's built-in lease/TTL mechanisms
- Implement rotation scripts for external secrets
- Test rotation in staging before production
- Maintain rollback capability during rotation

### Zero-Downtime Rotation
1. Generate new secret (old still valid)
2. Update consumers to use new secret
3. Verify all consumers switched
4. Revoke old secret

### Emergency Rotation
Triggered when:
- Secret suspected compromised
- Employee departure (with access)
- Security incident detected
- Audit finding requires immediate action

## Audit Log Analysis

### Suspicious Patterns
- Access outside business hours
- Access from unusual IP addresses
- Bulk secret reads (potential exfiltration)
- Failed authentication attempts (brute force)
- Access to secrets outside normal role scope
- Root token usage in production

### Compliance Requirements
- SOC 2: Audit logs retained 1 year minimum
- HIPAA: Access logs for PHI-related secrets
- PCI-DSS: Quarterly access reviews
- GDPR: Data processing records for encrypted PII
