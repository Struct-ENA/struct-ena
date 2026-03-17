<div align="center">

<img src="https://github.com/Struct-ENA/struct-ena.github.io/blob/main/paper_logo.png" width="120px"/>

### Struct-ENA: Modeling Structural Dynamics of Parent-Child Homework Interactions for Generative AI Simulations
<div>

[![Project Website](https://img.shields.io/badge/🌐-Project%20Website-0066CC?style=for-the-badge)](https://struct-ena.github.io/)
</div>

---

</div>

## 📌 Overview

> **Struct-ENA** is a computational framework designed to capture, model, and simulate the **structural dynamics** of parent-child interactions during homework activities. By leveraging **Epistemic Network Analysis (ENA)**, the project quantifies the evolving patterns of support, conflict, and guidance, providing a foundational architecture for high-fidelity **Generative AI simulations**.

This repository contains the orchestration logic used to transform behavioral interaction data into structural models that can drive AI-driven agents, simulating realistic educational scenarios within the home environment.

---

## ✨ Key Features

<div align="center">

### 🚀 Core Capabilities

</div>

<table>
<tr>
<td width="50%" valign="top">

#### 🎭 Structural Dynamics Modeling
Maps the fluid transitions and relational shifts in parent-child dyads, identifying key "interaction states" through high-dimensional structural analysis.

#### 🤖 Generative AI Simulation Bridge
Provides a standardized output format designed to prime LLMs and generative agents, enabling them to simulate homework help sessions with human-like structural consistency.

</td>
<td width="50%" valign="top">

#### 💾 Dynamic Interaction Memory
A collective state store that tracks the history of the interaction, preventing the "memory loss" typical in standard AI models when processing long, emotional, or complex sessions.

#### 🧪 Stress-Test Benchmarking
Evaluates how Generative AI models handle "Interference Loads"—such as contradictory instructions or emotional outbursts—within the simulated homework environment.

</td>
</tr>
</table>

---

## 🛠️ Getting Started

### 📦 1. Requirements

<div align="center">

| Requirement | Specification |
|:-----------:|:---------------------:|
| **Language** | Python 3.8+ |
| **API Support** | DeepSeek-R1 / Qwen3 / OpenAI-Compatible |

</div>

### ⚙️ 2. Configuration

Configure the **Collective Orchestration Framework (COF)** to define the simulation parameters and interaction weights.

<details>
<summary><b>📝 Click to view configuration example</b></summary>

```python
# Simulation Configuration for Parent-Child Interaction
interaction_settings = {
    "framework": "Struct-ENA",
    "dyad_type": "parent-child",
    "context": "mathematics_homework",
    "enable_emotional_dynamics": True,
    "max_iterations": 100
}

# Initialize the Collective Orchestration Framework (COF)
orchestrator = StructENA.COF(settings=interaction_settings)
