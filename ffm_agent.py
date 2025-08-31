import requests
import pandas as pd

# --------------------
# SETTINGS
# --------------------
preselected_names = ["M.Salah", "Gabriel", "Sánchez", "Cucurella", "Virgil"]
budget = 1000  # 100.0m in tenths (100m)

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
# BUILD FULL 15-MAN SQUAD
# --------------------
formation = {"GK": 1, "DEF": 2, "MID": 4, "FWD": 2}

for pos, count in formation.items():
    best = players[~players['id'].isin(preselected['id'])]
    best = best[best['position'] == pos].nlargest(count, 'score')
    selected.append(best)

squad = pd.concat(selected).drop_duplicates("id").head(15)
total_cost = squad['now_cost'].sum() / 10

# --------------------
# PICK STARTING XI (valid formation)
# --------------------
starting_xi = []

# 1 GK (best one)
gk = squad[squad['position'] == "GK"].nlargest(1, 'score')
starting_xi.append(gk)

# At least 3 DEF
defs = squad[squad['position'] == "DEF"].nlargest(3, 'score')
starting_xi.append(defs)

# At least 2 MID
mids = squad[squad['position'] == "MID"].nlargest(2, 'score')
starting_xi.append(mids)

# At least 1 FWD
fwds = squad[squad['position'] == "FWD"].nlargest(1, 'score')
starting_xi.append(fwds)

# Fill remaining spots (11 total)
remaining_needed = 11 - sum(len(df) for df in starting_xi)
used_ids = pd.concat(starting_xi)['id']
remaining_players = squad[~squad['id'].isin(used_ids)].nlargest(remaining_needed, 'score')
starting_xi.append(remaining_players)

starting_xi = pd.concat(starting_xi)

# --------------------
# CAPTAIN & VICE
# --------------------
captain = starting_xi.nlargest(1, 'score').iloc[0]
vice_captain = starting_xi.nlargest(2, 'score').iloc[1]

# --------------------
# PRINT RESULTS
# --------------------
print("\n🏆 Full 15-Man Squad:\n")
for _, p in squad.iterrows():
    star = "⭐" if p['web_name'] in preselected_names else ""
    print(f"{p['web_name']} - {p['team_name']} ({p['position']}) | "
          f"Form: {p['form']} | PPG: {p['points_per_game']} | "
          f"Price: {p['now_cost']/10}m {star}")

print(f"\n💰 Squad Total Cost: {total_cost:.1f}m")

print("\n🔮 Suggested Starting XI:\n")
for _, p in starting_xi.iterrows():
    cap = " (C)" if p['id'] == captain['id'] else ""
    vcap = " (VC)" if p['id'] == vice_captain['id'] else ""
    star = "⭐" if p['web_name'] in preselected_names else ""
    print(f"{p['web_name']} - {p['team_name']} ({p['position']}) "
          f"| Form: {p['form']} | PPG: {p['points_per_game']} | "
          f"Price: {p['now_cost']/10}m{cap}{vcap} {star}")
