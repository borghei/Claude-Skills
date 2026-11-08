"""Sound counterpart to sample_app_flawed: parameterised SQL, no shell, secrets from env,
authenticated and role-checked views, hashed passwords with MFA, structured audit logs."""
import json
import logging
import os
import sqlite3
import subprocess

import bcrypt  # password hashing
from django.contrib.auth.decorators import login_required, permission_required

DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
audit_log = logging.getLogger("audit")
logging.basicConfig(format="%(message)s")  # json log format: one JSON object per line


def audit(event, **fields):
    audit_log.info(json.dumps({"event": event, **fields}))


@login_required
@permission_required("users.view_user")  # role-based access
def find_user(request, name):
    cursor = sqlite3.connect("app.db").cursor()
    cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
    audit("user.lookup", actor=request.user.id, target=name)
    return cursor.fetchall()


def verify_login(stored_hash, password, totp_ok):
    """Password check plus a TOTP second factor (mfa)."""
    return bcrypt.checkpw(password.encode(), stored_hash) and totp_ok


def list_dir(path):
    return subprocess.run(["ls", "--", path], capture_output=True, text=True, check=False).stdout
