# Agent Testing Suite

> 🧪 Production-grade automated testing framework for AI agents

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)

## 🎯 What is this?

Don't ship broken agents to production. Agent Testing Suite helps you:
- ✅ Validate agent behavior before deployment
- 🐛 Catch regressions when updating prompts
- 🛡️ Test safety and compliance
- 📈 Benchmark performance
- 🔒 Ensure reliability at scale

## 🚀 Quick Start

```bash
# Install
pip install -r requirements.txt

# Create your first test
cat > test_greeting.yaml << 'EOF'
test:
  name: "Agent greets user politely"
  input: "Hello, who are you?"
  expected:
    assertions:
      - type: contains
        value: "help"
      - type: length
        max: 500
EOF

# Run tests
python test_suite.py demo
```

## 💰 Pricing

| Plan | Price | Test Runs | Best For |
|------|-------|-----------|----------|
| **Free** | $0 | 100/mo | Side projects |
| **Pro** | $79/mo | Unlimited | Professional teams |
| **Enterprise** | $499/mo | Unlimited | Enterprise QA |

## ✨ Features

- 📝 **YAML-based Tests** - Easy to write and maintain
- 🔍 **12+ Assertion Types** - From simple contains to LLM evaluation
- 🧠 **Semantic Testing** - Test meaning, not just text
- ⚡ **Parallel Execution** - Fast test runs
- 📊 **Beautiful Reports** - HTML, JSON, JUnit output
- 🔗 **CI/CD Ready** - GitHub Actions, GitLab CI, etc.
- 🎭 **Adversarial Tests** - Auto-generated safety tests

## 📖 Documentation

See [SKILL.md](SKILL.md) for complete documentation.

## 🛟 Support

- **Pro**: support@agentmesh.io
- **Enterprise**: Dedicated test engineer

## 💳 Payment

Subscribe at: https://paypal.me/keeganwattsmusic

Include your organization email in the payment note for provisioning.

---

Test smarter. Ship confidently.