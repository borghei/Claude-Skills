// Sample entry point for onboarding_generator.py.
import { createServer } from "node:http";

createServer((_req, res) => res.end("ok")).listen(3000);
