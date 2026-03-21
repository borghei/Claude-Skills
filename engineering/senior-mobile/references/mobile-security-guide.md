# Mobile Security Best Practices

Comprehensive security reference covering secure storage, network security, authentication, code protection, and compliance with OWASP Mobile Top 10.

---

## Secure Storage

### iOS: Keychain Services

The Keychain is the only secure storage on iOS. Never store secrets in `UserDefaults`, plist files, or plain files.

```swift
import Security

enum KeychainError: Error {
    case duplicateItem, itemNotFound, unexpectedStatus(OSStatus)
}

struct KeychainManager {
    static func save(key: String, data: Data, accessibility: CFString = kSecAttrAccessibleWhenUnlockedThisDeviceOnly) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: accessibility,
        ]

        let status = SecItemAdd(query as CFDictionary, nil)

        if status == errSecDuplicateItem {
            // Update existing
            let updateQuery: [String: Any] = [
                kSecClass as String: kSecClassGenericPassword,
                kSecAttrAccount as String: key,
            ]
            let attributes: [String: Any] = [kSecValueData as String: data]
            let updateStatus = SecItemUpdate(updateQuery as CFDictionary, attributes as CFDictionary)
            guard updateStatus == errSecSuccess else {
                throw KeychainError.unexpectedStatus(updateStatus)
            }
        } else if status != errSecSuccess {
            throw KeychainError.unexpectedStatus(status)
        }
    }

    static func read(key: String) throws -> Data {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne,
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess, let data = result as? Data else {
            throw KeychainError.itemNotFound
        }

        return data
    }

    static func delete(key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
        ]
        SecItemDelete(query as CFDictionary)
    }
}
```

**Keychain Accessibility Levels:**

| Level | When Available | Backup |
|-------|---------------|--------|
| `kSecAttrAccessibleWhenUnlocked` | Device unlocked | Yes |
| `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` | Device unlocked | No |
| `kSecAttrAccessibleAfterFirstUnlock` | After first unlock | Yes |
| `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` | After first unlock | No |

### Android: EncryptedSharedPreferences

```kotlin
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SecureStorage(context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val sharedPreferences = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
    )

    fun saveToken(token: String) {
        sharedPreferences.edit().putString("auth_token", token).apply()
    }

    fun getToken(): String? {
        return sharedPreferences.getString("auth_token", null)
    }

    fun clear() {
        sharedPreferences.edit().clear().apply()
    }
}
```

### Android: Keystore System

For cryptographic keys, use the Android Keystore:

```kotlin
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.spec.GCMParameterSpec

class CryptoManager {
    private val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }

    private fun getOrCreateKey(alias: String): javax.crypto.SecretKey {
        keyStore.getKey(alias, null)?.let { return it as javax.crypto.SecretKey }

        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore"
        )
        keyGenerator.init(
            KeyGenParameterSpec.Builder(alias,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setUserAuthenticationRequired(false)
                .build()
        )
        return keyGenerator.generateKey()
    }

    fun encrypt(data: ByteArray, alias: String = "default_key"): Pair<ByteArray, ByteArray> {
        val key = getOrCreateKey(alias)
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, key)
        return cipher.iv to cipher.doFinal(data)
    }

    fun decrypt(iv: ByteArray, encryptedData: ByteArray, alias: String = "default_key"): ByteArray {
        val key = getOrCreateKey(alias)
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.DECRYPT_MODE, key, GCMParameterSpec(128, iv))
        return cipher.doFinal(encryptedData)
    }
}
```

### React Native Secure Storage

```typescript
// Use react-native-keychain (wraps Keychain + Android Keystore)
import * as Keychain from 'react-native-keychain';

// Save credentials
await Keychain.setGenericPassword('username', 'authToken', {
  accessControl: Keychain.ACCESS_CONTROL.BIOMETRY_ANY,
  accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
});

// Read credentials
const credentials = await Keychain.getGenericPassword();
if (credentials) {
  console.log(credentials.password); // authToken
}

// Delete
await Keychain.resetGenericPassword();
```

---

## Certificate Pinning

### Why Certificate Pinning

Prevents man-in-the-middle attacks by validating the server's certificate against a known set of certificates or public keys, even when the device trusts a rogue CA.

### iOS: URLSession Pinning

```swift
class PinnedURLSessionDelegate: NSObject, URLSessionDelegate {
    private let pinnedCertificates: [SecCertificate]

    init(certificateNames: [String]) {
        pinnedCertificates = certificateNames.compactMap { name in
            guard let url = Bundle.main.url(forResource: name, withExtension: "cer"),
                  let data = try? Data(contentsOf: url),
                  let cert = SecCertificateCreateWithData(nil, data as CFData)
            else { return nil }
            return cert
        }
    }

    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Set pinned certificates as trusted anchors
        SecTrustSetAnchorCertificates(serverTrust, pinnedCertificates as CFArray)

        var error: CFError?
        if SecTrustEvaluateWithError(serverTrust, &error) {
            completionHandler(.useCredential, URLCredential(trust: serverTrust))
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}
```

### Android: OkHttp Certificate Pinning

```kotlin
val client = OkHttpClient.Builder()
    .certificatePinner(
        CertificatePinner.Builder()
            .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
            .add("api.example.com", "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=") // backup
            .build()
    )
    .build()
```

### React Native (TrustKit or react-native-ssl-pinning)

```typescript
import { fetch as pinnedFetch } from 'react-native-ssl-pinning';

const response = await pinnedFetch('https://api.example.com/data', {
  method: 'GET',
  sslPinning: {
    certs: ['my_cert'], // .cer files in native assets
  },
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Certificate Pinning Best Practices

- **Pin the public key** (not the certificate) for easier rotation
- **Include backup pins** (at least 2) to avoid lockout during rotation
- **Set a max-age** so pins expire if not updated
- **Have a remote kill switch** to disable pinning if pins become invalid
- **Test certificate rotation** in staging before production
- **Monitor pinning failures** via server-side logging

---

## Code Obfuscation

### iOS

- **Bitcode:** Deprecated as of Xcode 14; no longer needed
- **Symbol stripping:** Enabled by default in release builds
- **String encryption:** Use third-party tools (iXGuard, SwiftShield)

```
# Build Settings (already default for Release)
STRIP_INSTALLED_PRODUCT = YES
STRIP_STYLE = all
DEPLOYMENT_POSTPROCESSING = YES
```

### Android: R8/ProGuard

```proguard
# proguard-rules.pro

# Keep model classes (used with Gson/Moshi)
-keep class com.example.myapp.data.remote.dto.** { *; }
-keep class com.example.myapp.domain.model.** { *; }

# Keep Hilt-generated code
-keep class dagger.hilt.** { *; }
-keep class javax.inject.** { *; }

# Obfuscate everything else
-repackageclasses ''
-allowaccessmodification
-optimizations !code/simplification/arithmetic

# Remove logging
-assumenosideeffects class android.util.Log {
    public static int d(...);
    public static int v(...);
    public static int i(...);
}
```

### React Native: Hermes Bytecode

Hermes compiles JS to bytecode, providing basic obfuscation:

```json
// app.json
{
  "expo": {
    "jsEngine": "hermes"
  }
}
```

For additional protection:
- Use `react-native-obfuscating-transformer` for JS obfuscation
- Enable ProGuard/R8 for the Android Java/Kotlin layer
- Strip debug symbols in release builds

---

## Biometric Authentication

### iOS: LocalAuthentication

```swift
import LocalAuthentication

class BiometricManager {
    enum BiometricType {
        case none, touchID, faceID, opticID
    }

    static var biometricType: BiometricType {
        let context = LAContext()
        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: nil) else {
            return .none
        }
        switch context.biometryType {
        case .touchID: return .touchID
        case .faceID: return .faceID
        case .opticID: return .opticID
        default: return .none
        }
    }

    static func authenticate(reason: String) async throws -> Bool {
        let context = LAContext()
        context.localizedCancelTitle = "Use Password"

        return try await context.evaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            localizedReason: reason
        )
    }
}

// Usage
Task {
    do {
        let success = try await BiometricManager.authenticate(
            reason: "Authenticate to access your account"
        )
        if success { /* unlock */ }
    } catch {
        // Fall back to password
    }
}
```

**Info.plist requirement:**
```xml
<key>NSFaceIDUsageDescription</key>
<string>We use Face ID to securely authenticate you.</string>
```

### Android: BiometricPrompt

```kotlin
import androidx.biometric.BiometricPrompt

class BiometricHelper(
    private val activity: FragmentActivity,
    private val onSuccess: () -> Unit,
    private val onError: (String) -> Unit,
) {
    private val executor = ContextCompat.getMainExecutor(activity)

    private val callback = object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
            onSuccess()
        }

        override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
            onError(errString.toString())
        }

        override fun onAuthenticationFailed() {
            onError("Authentication failed")
        }
    }

    fun authenticate() {
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Biometric Authentication")
            .setSubtitle("Verify your identity")
            .setAllowedAuthenticators(
                BiometricManager.Authenticators.BIOMETRIC_STRONG or
                BiometricManager.Authenticators.DEVICE_CREDENTIAL
            )
            .build()

        BiometricPrompt(activity, executor, callback).authenticate(promptInfo)
    }
}
```

### React Native: expo-local-authentication

```typescript
import * as LocalAuthentication from 'expo-local-authentication';

async function authenticateWithBiometrics(): Promise<boolean> {
  // Check hardware support
  const hasHardware = await LocalAuthentication.hasHardwareAsync();
  if (!hasHardware) return false;

  // Check if biometrics are enrolled
  const isEnrolled = await LocalAuthentication.isEnrolledAsync();
  if (!isEnrolled) return false;

  // Authenticate
  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: 'Verify your identity',
    cancelLabel: 'Use Password',
    disableDeviceFallback: false,
  });

  return result.success;
}
```

---

## Network Security Configuration

### Android: network_security_config.xml

```xml
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- Disable cleartext traffic globally -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <!-- Pin certificates for your API domain -->
    <domain-config>
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2026-12-31">
            <pin digest="SHA-256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
            <pin digest="SHA-256">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</pin>
        </pin-set>
    </domain-config>

    <!-- Allow cleartext for local development only -->
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="false">10.0.2.2</domain>
        <domain includeSubdomains="false">localhost</domain>
    </domain-config>
</network-security-config>
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
```

### iOS: App Transport Security (ATS)

ATS is enabled by default. Avoid disabling it globally.

```xml
<!-- Info.plist - only add exceptions for specific domains -->
<key>NSAppTransportSecurity</key>
<dict>
    <!-- Do NOT set NSAllowsArbitraryLoads to true -->
    <key>NSExceptionDomains</key>
    <dict>
        <key>legacy-api.example.com</key>
        <dict>
            <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
            <true/>
            <key>NSTemporaryExceptionMinimumTLSVersion</key>
            <string>TLSv1.2</string>
        </dict>
    </dict>
</dict>
```

### Secure API Communication Checklist

- [ ] All traffic over HTTPS (TLS 1.2 minimum, prefer 1.3)
- [ ] Certificate pinning for primary API domains
- [ ] Token-based authentication (JWT with short expiry)
- [ ] Refresh tokens stored in secure storage (Keychain / Keystore)
- [ ] Request signing for sensitive operations
- [ ] Rate limiting awareness (handle 429 responses gracefully)
- [ ] No sensitive data in URL query parameters (use POST body or headers)
- [ ] Timeouts configured to prevent hanging connections

---

## OWASP Mobile Top 10 (2024)

### M1: Improper Credential Usage

**Risk:** Hardcoded credentials, insecure token storage, weak authentication.

**Mitigations:**
- Never hardcode API keys, secrets, or passwords in source code
- Store credentials in Keychain (iOS) or Keystore (Android)
- Use short-lived tokens with refresh mechanism
- Implement token revocation on logout
- Use certificate pinning for credential transmission

### M2: Inadequate Supply Chain Security

**Risk:** Vulnerable or malicious third-party libraries.

**Mitigations:**
- Audit dependencies regularly (`npm audit`, `bundle audit`, `dependabot`)
- Lock dependency versions (lockfiles)
- Use only well-maintained, widely-adopted libraries
- Review library permissions and code for suspicious behavior
- Enable integrity checks (npm `package-lock.json` integrity field)

### M3: Insecure Authentication/Authorization

**Risk:** Weak login flows, missing session management, client-side auth bypasses.

**Mitigations:**
- Perform all authorization checks server-side
- Implement proper session timeout and refresh
- Use multi-factor authentication for sensitive operations
- Lock accounts after failed attempts
- Never trust client-side validation alone

### M4: Insufficient Input/Output Validation

**Risk:** Injection attacks, XSS via WebViews, data corruption.

**Mitigations:**
- Validate and sanitize all user inputs
- Use parameterized queries for local databases (Room, Core Data)
- Sanitize HTML content before rendering in WebViews
- Validate deep link parameters before processing
- Implement input length limits

### M5: Insecure Communication

**Risk:** Cleartext traffic, missing certificate validation, data interception.

**Mitigations:**
- Enforce HTTPS everywhere (ATS on iOS, network_security_config on Android)
- Implement certificate pinning
- Do not disable SSL/TLS validation (even in development)
- Avoid transmitting sensitive data in URLs
- Use end-to-end encryption for highly sensitive data

### M6: Inadequate Privacy Controls

**Risk:** Excessive data collection, missing consent, data leakage.

**Mitigations:**
- Collect only necessary data (data minimization)
- Implement proper consent flows (GDPR, CCPA)
- Provide data deletion capability
- Clear sensitive data from clipboard, screenshots, and logs
- Disable screenshots for sensitive screens:

```swift
// iOS: Hide content in app switcher
func sceneWillResignActive(_ scene: UIScene) {
    let blurView = UIVisualEffectView(effect: UIBlurEffect(style: .light))
    blurView.tag = 999
    window?.addSubview(blurView)
    blurView.frame = window?.bounds ?? .zero
}

func sceneDidBecomeActive(_ scene: UIScene) {
    window?.viewWithTag(999)?.removeFromSuperview()
}
```

```kotlin
// Android: Prevent screenshots
window.setFlags(
    WindowManager.LayoutParams.FLAG_SECURE,
    WindowManager.LayoutParams.FLAG_SECURE
)
```

### M7: Insufficient Binary Protections

**Risk:** Reverse engineering, code tampering, repackaging.

**Mitigations:**
- Enable code obfuscation (R8/ProGuard on Android)
- Strip debug symbols in release builds
- Implement runtime integrity checks (jailbreak/root detection)
- Use tamper detection libraries
- Avoid storing business logic exclusively on the client

### M8: Security Misconfiguration

**Risk:** Debug features in production, exposed admin endpoints, default credentials.

**Mitigations:**
- Remove all debug logs and test code before release
- Disable WebView debugging in production
- Review exported components and content providers (Android)
- Set `android:debuggable="false"` in release builds
- Review URL schemes for hijacking potential

### M9: Insecure Data Storage

**Risk:** Sensitive data in plaintext files, logs, backups, or caches.

**Mitigations:**
- Use encrypted storage for all sensitive data
- Exclude sensitive files from device backups
- Clear sensitive data from memory when no longer needed
- Disable keyboard caching for sensitive input fields
- Review application logs for sensitive data exposure

```swift
// iOS: Exclude from backup
var url = getDocumentsDirectory().appendingPathComponent("sensitive.dat")
var resourceValues = URLResourceValues()
resourceValues.isExcludedFromBackup = true
try url.setResourceValues(resourceValues)
```

```kotlin
// Android: Exclude from backup
// AndroidManifest.xml
android:allowBackup="false"
android:fullBackupContent="@xml/backup_rules"

// res/xml/backup_rules.xml
<full-backup-content>
    <exclude domain="sharedpref" path="secure_prefs.xml" />
    <exclude domain="database" path="sensitive.db" />
</full-backup-content>
```

### M10: Insufficient Cryptography

**Risk:** Weak algorithms, hardcoded keys, improper key management.

**Mitigations:**
- Use platform cryptography (CommonCrypto on iOS, Android Keystore)
- Never implement custom cryptographic algorithms
- Use AES-256-GCM for symmetric encryption
- Use RSA-2048+ or ECDSA for asymmetric encryption
- Store cryptographic keys in hardware-backed storage (Secure Enclave / StrongBox)
- Never hardcode encryption keys in source code
- Rotate keys periodically

---

## Security Audit Checklist

### Pre-Release Security Review

- [ ] No hardcoded secrets in source code (scan with tools like `gitleaks`)
- [ ] All API keys stored in environment variables / secure config
- [ ] Certificate pinning implemented and tested
- [ ] Biometric authentication tested on real devices
- [ ] Sensitive screens prevent screenshots
- [ ] Debug logging removed from release builds
- [ ] ProGuard/R8 enabled for Android release
- [ ] ATS not globally disabled on iOS
- [ ] Network security config restricts cleartext traffic
- [ ] Secure storage used for tokens and credentials
- [ ] Input validation on all user-provided data
- [ ] Deep link parameters validated and sanitized
- [ ] Backup exclusions configured for sensitive data
- [ ] Third-party dependencies audited for vulnerabilities
- [ ] Root/jailbreak detection implemented (if required)
- [ ] SSL/TLS minimum version set to 1.2
- [ ] Session timeout and token refresh implemented
- [ ] Privacy policy and data handling documented
- [ ] Penetration testing completed for critical flows
