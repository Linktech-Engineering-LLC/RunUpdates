# Contributing to RunUpdates

Thank you for your interest in contributing to RunUpdates!  
This project is part of the Linktech Engineering Tools Suite and follows a deterministic, operator‑grade engineering philosophy.

We welcome contributions that improve clarity, correctness, maintainability, and reproducibility.

---

## 🧭 Philosophy

RunUpdates is built around:

- deterministic behavior  
- clean, structured logging  
- predictable execution  
- minimal dependencies  
- audit‑friendly output  
- explicit configuration (no magic)  

Please keep these principles in mind when proposing changes.

---

## 🛠 How to Contribute

### 1. Fork the repository

```bash
git clone https://github.com/Linktech-Engineering-LLC/RunUpdates.git
cd RunUpdates
```

### 2. Create a feature branch

```bash
git checkout -b feature/my-improvement
```

### 3. Make your changes

Please ensure:

- no breaking changes to the inventory schema
- no hidden behavior or implicit defaults
- logging remains structured and operator‑grade
- code is deterministic and reproducible
- functions remain small and explicit
- no unnecessary dependencies are introduced

### 4. Run linting (if configured)

```bash
ruff check .
```

### 5. Submit a pull request

Your PR should include:

- a clear description of the change
- why it improves the project
- any relevant test cases or examples
- confirmation that it does not break existing inventories

## 📦 Inventory Schema Stability

The inventory schema is considered **stable**.
Changes to the schema require:

- discussion in an issue
- version bump
- migration notes
- README updates

Please avoid adding complexity unless it provides clear operational value.

## 🔐 Secrets Handling

Do not include:

- real hostnames
- real usernames
- real passwords
- real SSH keys
- vault files

Use placeholders in examples.

## 🧪 Testing Guidelines

When adding new features:

- test both LocalSession and SSHSession paths
- test dry‑run mode
- test inventory flattening
- test host selection logic
- test error handling and logging output

## 🗂 Project Structure

Key components:

```code
operations/
  selector.py
  connector.py
  executor.py
  orchestrator.py
  sessions.py
inventory/
  sample-inventory.yaml
main.py
```

Please keep new modules consistent with this structure.

## 🤝 Code of Conduct

Be respectful, constructive, and collaborative.
We’re building tools for real operators — clarity and professionalism matter.

## 📄 License
By contributing, you agree that your contributions will be licensed under the MIT License.