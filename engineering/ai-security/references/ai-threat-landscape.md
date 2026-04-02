# AI Threat Landscape Reference

## Overview

This reference covers the primary threat categories affecting AI/ML systems, based on OWASP Top 10 for LLMs, MITRE ATLAS, and NIST AI Risk Management Framework.

## 1. Prompt Injection

### Direct Prompt Injection
An attacker crafts input that overrides system instructions.

**Attack Vectors:**
- Instruction override: "Ignore previous instructions and..."
- Role manipulation: "You are now a different assistant that..."
- Context poisoning: Embedding hidden instructions in seemingly benign content
- Encoding tricks: Base64, ROT13, or Unicode obfuscation of malicious instructions

**Mitigations:**
- Input sanitization and validation before prompt assembly
- Delimiter-based prompt structure with clear boundaries
- Output filtering to detect instruction leakage
- Least-privilege system prompts
- Input length limits

### Indirect Prompt Injection
Malicious instructions embedded in external data the model processes.

**Attack Vectors:**
- Poisoned web content retrieved by RAG systems
- Malicious documents uploaded for analysis
- Compromised API responses fed to the model
- Hidden text in images processed by vision models

**Mitigations:**
- Validate and sanitize all external data sources
- Separate data plane from control plane in prompts
- Monitor for unexpected tool/function calls
- Content integrity verification for retrieved documents

## 2. Data Poisoning

### Training Data Poisoning
Manipulating training data to introduce backdoors or biases.

**Attack Vectors:**
- Backdoor injection: Adding trigger patterns that cause specific outputs
- Label flipping: Changing labels to degrade model accuracy
- Data injection: Adding crafted samples to public datasets
- Gradient-based poisoning: Optimized perturbations to training data

**Mitigations:**
- Data provenance tracking and integrity verification
- Statistical anomaly detection on training datasets
- Data sanitization pipelines
- Federated learning with robust aggregation
- Regular model auditing against known benchmarks

### Fine-tuning Poisoning
Corrupting models during fine-tuning or RLHF phases.

**Attack Vectors:**
- Malicious fine-tuning datasets from untrusted sources
- Reward hacking in RLHF pipelines
- Adapter/LoRA poisoning

**Mitigations:**
- Verify fine-tuning data sources
- Monitor model behavior drift during fine-tuning
- A/B testing against baseline models
- Automated red-teaming after fine-tuning

## 3. Model Extraction

### Model Stealing
Replicating a model's functionality through query access.

**Attack Vectors:**
- Systematic querying to build training dataset for a clone
- Exploiting confidence scores and logits
- Side-channel attacks on model serving infrastructure
- API response analysis to infer architecture

**Mitigations:**
- Rate limiting on inference endpoints
- Minimize output information (avoid returning logits/probabilities)
- Query pattern monitoring and anomaly detection
- Watermarking model outputs
- Authentication and usage tracking

## 4. Adversarial Inputs

### Evasion Attacks
Crafted inputs that cause incorrect model predictions.

**Attack Vectors:**
- Perturbation attacks (FGSM, PGD, C&W)
- Semantic adversarial examples
- Transfer attacks from surrogate models
- Physical-world adversarial patches

**Mitigations:**
- Adversarial training
- Input preprocessing and denoising
- Ensemble methods
- Certified robustness techniques
- Input anomaly detection

## 5. Insecure Model Serving

### Deserialization Attacks
Exploiting unsafe model loading mechanisms.

**Attack Vectors:**
- Pickle-based model files with embedded code execution
- Malicious ONNX models with custom operators
- Compromised model registries
- Supply chain attacks on model dependencies

**Mitigations:**
- Use safe serialization formats (SafeTensors, JSON)
- Verify model checksums and signatures
- Scan models before loading
- Isolated model execution environments
- Pin model versions with hash verification

## 6. Severity Classification

| Severity | Description | Response Time |
|----------|-------------|---------------|
| CRITICAL | Active exploitation possible, data exfiltration risk | Immediate |
| HIGH | Exploitable with moderate effort, significant impact | 24-48 hours |
| MEDIUM | Requires specific conditions, moderate impact | 1-2 weeks |
| LOW | Theoretical risk, minimal impact | Next sprint |

## 7. Compliance Frameworks

- **OWASP Top 10 for LLM Applications** (2025)
- **MITRE ATLAS** - Adversarial Threat Landscape for AI Systems
- **NIST AI RMF** - AI Risk Management Framework
- **EU AI Act** - Risk classification and requirements
- **ISO 42001** - AI Management System standard
