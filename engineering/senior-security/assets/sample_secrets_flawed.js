// Deliberately flawed fixture for secret_scanner.py. The AWS key is Amazon's published
// documentation example (AKIAIOSFODNN7EXAMPLE), not a real credential.
const config = {
  awsAccessKeyId: "AKIAIOSFODNN7EXAMPLE",
  dbPassword: "correct-horse-battery-staple",
  apiBase: "https://api.example.com",
};

module.exports = config;
