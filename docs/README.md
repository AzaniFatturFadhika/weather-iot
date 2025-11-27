# Documentation Index

Welcome to the Weather IoT Monitoring System documentation!

---

## 📚 Documentation Categories

### 🚀 [Guides](guides/) - For Users & Operators
Get started and learn how to use the system.

| Guide | Description |
|-------|-------------|
| [Getting Started](guides/getting-started.md) | **NEW** - Complete setup from scratch |
| [Quick Start](guides/quick-start.md) | **NEW** - TL;DR version for experienced users |
| [Adding Transmitter](guides/adding-transmitter.md) | How to add new weather station |
| [Mosquitto Setup](guides/mosquitto-setup.md) | MQTT broker installation (WSL) |
| [Troubleshooting](guides/troubleshooting.md) | **NEW** - Common problems & solutions |

---

### 🏗️ [Architecture](architecture/) - System Design
Understand how everything works together.

| Document | Description |
|----------|-------------|
| [Multi-Transmitter System](architecture/multi-transmitter.md) | Station registry & scalability |
| [Data Format Standard](architecture/data-format.md) | Industry standards & compliance |
| [Production Deployment](architecture/production-deployment.md) | Real-world implementation |
| [System Overview](architecture/system-overview.md) | **NEW** - High-level architecture |

---

### 📡 [API Reference](api/) - Data Formats & Integration
Technical specs for developers.

| Document | Description |
|----------|-------------|
| [JSON Schema](api/json-schema.md) | **NEW** - Complete JSON format reference |
| [MQTT Topics](api/mqtt-topics.md) | **NEW** - Topic structure & usage |
| [LoRa Payload](api/lora-payload.md) | **NEW** - Transmitter payload format |

---

### 🔧 [Hardware](hardware/) - Physical Components
Hardware specifications and assembly.

| Document | Description |
|----------|-------------|
| [Pin Reference](hardware/pin-reference.md) | ESP32 & Arduino pin connections |
| [Parts List](hardware/parts-list.md) | **NEW** - Complete BOM |
| [Assembly Guide](hardware/assembly-guide.md) | **NEW** - Step-by-step build |

---

### 💻 [Development](development/) - For Contributors
Resources for developers working on the codebase.

| Document | Description |
|----------|-------------|
| [MQTT Library Comparison](development/mqtt-library-comparison.md) | Library selection rationale |
| [Contributing Guide](development/contributing.md) | **NEW** - How to contribute |
| [Testing Guide](development/testing.md) | **NEW** - Testing procedures |

---

### 📝 [Changelog](changelog/) - Version History
Track changes across versions.

| Version | Description |
|---------|-------------|
| [v2.0.0](changelog/v2.0.0.md) | Industry Standard Compliant |
| [v1.0.0](changelog/v1.0.0.md) | **NEW** - Initial release notes |
| [Format Audit](changelog/audit-format-data.md) | Data format compliance analysis |

---

## 🎯 Find What You Need

### I want to...

**...get started quickly**  
→ [Quick Start Guide](guides/quick-start.md)

**...understand the system**  
→ [System Overview](architecture/multi-transmitter.md)

**...integrate with my application**  
→ [JSON Schema](api/json-schema.md)

**...build the hardware**  
→ [Pin Reference](hardware/pin-reference.md) + [Parts List](hardware/parts-list.md)

**...troubleshoot problems**  
→ [Troubleshooting Guide](guides/troubleshooting.md)

**...add a new transmitter**  
→ [Adding Transmitter Guide](guides/adding-transmitter.md)

**...deploy to production**  
→ [Production Deployment](architecture/production-deployment.md)

**...contribute code**  
→ [Contributing Guide](development/contributing.md)

---

## 📊 Documentation Status

| Category | Files | Status |
|----------|-------|--------|
| Guides | 5 | ⚠️ 3 pending |
| Architecture | 4 | ⚠️ 1 pending |
| API | 3 | ⚠️ 3 pending |
| Hardware | 3 | ⚠️ 2 pending |
| Development | 3 | ⚠️ 2 pending |
| Changelog | 3 | ✅ Complete |

**Legend:** ✅ Complete | ⚠️ In Progress | ❌ Not Started

---

## 🔍 Search Tips

- Use Ctrl+F to search within documents
- Check the [main README](../README.md) for quick links
- File an [issue](https://github.com/your-username/weather-iot/issues) if documentation is unclear

---

**Last Updated:** 2025-11-23
