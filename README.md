# 🏆 Fantasy Premier League Agent

A Python-based script that analyzes Fantasy Premier League (FPL) data and suggests the **best starting XI** each gameweek.  
Supports **pre-selecting must-have players** (e.g., Haaland, Salah) and fills the rest of the squad optimally.

---

## ⚡ Features
- Fetches **live FPL player stats** from the official API  
- Builds a squad of **11 players** based on:
  - Form
  - Points per Game (PPG)
  - Player availability
- Allows **pre-selecting specific players** (always included in squad)  
- Prints team with total cost and key info  

---

## 📦 Requirements
- Python **3.10+** (tested on 3.10, works on 3.13)  
- Libraries:
  - `requests`
  - `pandas`

Install dependencies:
```bash
pip install requests pandas
