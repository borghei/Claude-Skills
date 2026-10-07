# Desktop, Mobile, and Local IPC Companion

Tier: full.

## Select this companion when

The target runs on a user's device and has boundaries there: native desktop
or mobile apps, custom URL schemes and deep links, web views with a native
bridge, exported app components, privileged helpers or services, local
daemons, and local channels such as Unix sockets, named pipes, loopback
ports, or platform IPC.

On a device the lower-trust actor is usually another app, a web page, a
document, or an unprivileged local user — not a remote network client.

## Ground rules

```text
- Name the local attacker precisely: a web page in the user's browser,
  another installed app without special permission, a file the user opens, an
  unprivileged account on a shared machine, or a second profile on the device.
- Name the boundary: app sandbox, user account, privilege level, web origin
  versus native code, signed-in account.
- An attacker who already has the victim's own privilege inside the same
  sandbox has crossed nothing. Say what they gain that they did not have.
- Platform defaults, entitlements granted at signing, and store review are
  outside the repository unless the manifest or project file declares them.
  Read those files; treat the rest as unknown.
- Reproduce in a local build, emulator, or test harness with dummy accounts,
  inside the sandbox the lead confirmed. Never install onto or probe a device
  you do not control.
```

## Hunting classes

### Custom scheme and deep link handling

Links any app or page can open that trigger an action or carry parameters
into navigation, a web view, a file path, or an API call. Check which hosts
and paths the handler accepts, how it parses them, and whether verified
link association is required or optional.

### App-to-app and account handoff

Sign-in callbacks, share targets, and "open in" flows where another app can
intercept the response, inject one of its own, or cause an action in an
account the user did not choose.

### File open and intent authority

Opening a file, a document type, or an incoming intent causes the app to act
with its own permissions on a path or resource the sender picked: reading
private files, overwriting data, importing configuration.

### Webview navigation reaching the bridge

A web view that exposes native functions and can be navigated to, or made to
load, content the app does not control: unchecked URLs, redirects, injected
frames, cleartext loads. Establish which origin can call which native method.

### Over-broad native bridge

Bridge methods that take paths, URLs, commands, or selectors from page script
and act on them with native privilege, without checking the caller or
constraining the argument.

### Webview file access

Web views allowed to read local files, cross from file to network origins, or
load content from shared storage, turning a script-injection or a crafted
file into a read of the app's private data.

### Local IPC peer authentication

A socket, pipe, loopback port, or platform service that accepts any local
caller. Check how the server identifies the peer — credentials from the
channel, code-signature checks, access control on the endpoint — and whether
a browser page can reach a loopback listener.

### Claimed identity versus channel identity

The service authenticates the connection one way and then trusts a user,
process, or bundle identifier supplied in the message. Identifiers that can
be reused or raced between check and use belong here.

### Exported components

Activities, services, receivers, providers, extension points, and scripting
interfaces reachable by other apps without a permission, or with one any app
can obtain. Follow what each does with caller-supplied data.

### IPC request lifecycle and correlation

Replies delivered to the wrong caller, callbacks retained after the caller
disconnects, requests accepted before initialization or after teardown, and
state shared between sessions of different clients.

### Privileged helper as confused deputy

A helper running with elevated rights performs file, process, network, or
configuration operations on request, using arguments the unprivileged caller
controls: paths, commands, package locations, environment.

### Install, update, and repair paths

Installers, updaters, and repair tools that run elevated and read from
user-writable locations, verify a package and then reopen it by path, or load
libraries from a directory the user controls.

### Local file ownership and races

Sensitive files created with permissive modes or in shared directories,
predictable temporary names, and check-then-open sequences an unprivileged
user can win with a link.

### Credential store boundaries

Secrets stored outside the platform's protected store, in a store entry
shared with other apps from the same vendor group, exported in backups, or
accessible while the device is locked when they should not be.

### Account switch, logout, and restore residue

Data, tokens, caches, notifications, or web-view state from one account
visible after switching or signing out, or restored onto a different device
or profile.

### Pending actions and user presence

A sensitive action queued or confirmed while the app was in one state and
completed in another: an approval surviving a lock, a prompt that another
window can cover or answer, a biometric check not tied to the action.

## Cross-cutting moves

- Enumerate every externally reachable entry from the manifest and project
  files before reading handlers.
- For each IPC endpoint, answer: who can connect, how is the peer identified,
  what is trusted from the message.
- Read privileged code as if every argument came from an attacker.
- Exercise lifecycle edges: first launch, backgrounded, locked, logged out,
  account switched, upgraded, restored from backup.
- Compare platforms. A check present on one and missing on its sibling is a
  unit.

## Evidence bar

- Confirmed needs a local reproduction: the crafted link, intent, message, or
  file, sent by a dummy lower-trust sender, and the privileged effect
  observed.
- Where the outcome depends on platform version, signing entitlements, or
  device policy not declared in the repository, record `needs_validation`.
- Actions that require the victim's own unlocked session and privilege, with
  no boundary crossed, are not findings.
- Severity follows the privilege gained: code execution as a higher-privilege
  user or theft of another app's or account's secrets is high.
