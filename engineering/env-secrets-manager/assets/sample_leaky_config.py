# Deliberately leaky file for secret_scanner.py. Every value below is fake:
# the AWS key is the documented example from AWS's own docs, the rest are made up.
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
DATABASE_URL = "postgres://admin:fake-pass-1234@db.example.internal:5432/app"
api_key = "fake-api-key-not-real-0000"


def connect():
    """Read credentials from the environment instead of the constants above."""
    import os
    return os.environ.get("DATABASE_URL")
