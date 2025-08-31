import requests
import pandas as pd

# --------------------
# SETTINGS
# --------------------
preselected_names = ["Haaland", "Salah"]   # change to any player web_name
budget = 1000  # 100.0m in tenths

# --------------------
# FETCH DATA
# --------------------
bootstrap_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
data = requests.get(bootstrap_url).json()

players = pd.DataFrame(data['elements'])
teams = pd.DataFrame(data['teams'])

players['team_name'] = players['team'].map(teams.set_index('id')['name'])
players['position'] = players['element_type'].map({
    1: "GK", 2: "DEF", 3: "MID", 4: "FWD"
})

players['score'] = players['form'].astype(float) + players['points_per_game'].astype(float)
players = players[players['status'] == "a"]  # only available players

# --------------------
# SELECT PRE-SELECTED
# --------------------
preselected = players[players['web_name'].isin(preselected_names)]
if len(preselected) < len(preselected_names):
    print("⚠️ Warning: Some preselected players not found or inactive.")

selected = [preselected]

# --------------------
# BASE FORMATION
# --------------------
formation = {"GK": 1, "DEF": 3, "MID": 3, "FWD": 1}

for pos, count in formation.items():
    best = players[~players['id'].isin(preselected['id'])]
    best = best[best['position'] == pos].nlargest(count, 'score')
    selected.append(best)

# --------------------
# FILL REMAINING SPOTS
# --------------------
remaining = pd.concat(selected)
needed = 11 - len(remaining)
extra = players[~players['id'].isin(remaining['id'])].nlargest(needed, 'score')
selected.append(extra)

# --------------------
# FINAL SQUAD
# --------------------
squad = pd.concat(selected)
total_cost = squad['now_cost'].sum() / 10

print("\n🔮 Suggested Starting XI (with preselected players):\n")
for _, p in squad.iterrows():
    star = "⭐" if p['web_name'] in preselected_names else ""
    print(f"{p['web_name']} - {p['team_name']} ({p['position']}) | "
          f"Form: {p['form']} | PPG: {p['points_per_game']} | "
          f"Price: {p['now_cost']/10}m {star}")

print(f"\n💰 Total Cost: {total_cost:.1f}m")
