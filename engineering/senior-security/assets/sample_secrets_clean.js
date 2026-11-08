// Clean fixture for secret_scanner.py: credentials come from the environment.
const config = {
  awsAccessKeyId: process.env.AWS_ACCESS_KEY_ID,
  dbPassword: process.env.DB_PASSWORD,
  apiBase: "https://api.example.com",
};

module.exports = config;
