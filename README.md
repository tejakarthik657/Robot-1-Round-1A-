# 🧠 Robot 1 (Round 1A) – PDF Outline Extractor

This project extracts a structured **Table of Contents (ToC)** — including **title, headings, and subheadings** — from any PDF file and outputs a clean **JSON outline**.

It is designed to be:
- 🚀 Fast (under 10 seconds for a 50-page file)
- 📦 Dockerized for portability
- 🛠️ Offline-first (no internet needed)
- 📂 Folder-based input/output

---

## 📁 Project Branches

| Branch Name               | Description                                       |
|---------------------------|---------------------------------------------------|
| `Robot-1-Round-1A`        | Main project code and Dockerized implementation  |
| `main`                    | Project overview and usage documentation         |

---

## 🧰 How it Works

1. Put your PDF files in the `/input/` folder.
2. Run the Docker container.
3. Get JSON output from the `/output/` folder.

The tool extracts:
- 📌 Document title (if available)
- 📌 Level 1 Headings (biggest font size)
- 📌 Level 2 & 3 Subheadings (based on font size hierarchy)

---

## 🐳 Quick Start with Docker

```bash
# Build Docker image
docker build -t pdf-outline .

# Run container with input/output folder mount
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-outline
