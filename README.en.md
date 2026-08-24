🇰🇷 [한국어](README.md) · 🇬🇧 **English**

# KORAIL Open Data MCP

A collection of MCP (Model Context Protocol) servers that connect Korea Railroad Corporation (KORAIL) public data to AI.
Once installed, you can query KORAIL data in natural language from Claude Desktop, Claude Code, Cursor, Antigravity, GitHub Copilot (CLI/VS Code), and other MCP clients.

> ✅ **No API key required** — a dedicated proxy server handles all public data API calls for you.
>
> 💻 **Local install (stdio)** — runs directly on your PC, no separate server needed. Connects to local MCP clients such as Claude Desktop, Claude Code, Cursor, Antigravity, and GitHub Copilot (CLI/VS Code). Web-only services like ChatGPT and Grok need a remote connection instead (see the Advanced section below).
>
> 📦 **Disk space needed** — about **100MB** (including the Python runtime and packages managed by `uv`)

> 👉 **New here?** Just follow the 3 install steps below. The full list of 98 tools further down is only for reference once you're set up.

---

## ⚙️ Installation (Windows · 2 steps)

No need to install Python separately or download the repository. **`uv` prepares everything it needs automatically.**

### Step 1 — Install uv (one-time)

Open PowerShell and paste the following. **Administrator rights are not required.**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installing, **open a new PowerShell window** — if `uv --version` prints a version, it worked.

### Step 2 — Install KORAIL MCP (one-time)

```powershell
uv tool install --from git+https://github.com/lovelyquality/korail-mcp.git korail-mcp
```

Success looks like `Installed 1 executable: korail-mcp` at the end.

> ⏳ The first install takes 1–3 minutes (downloading Python and packages). After that, startup takes **about 5 seconds**.
>
> 🔄 **Updating to the latest version** — run `uv tool upgrade korail-mcp`, then restart your client.

---

## 🔌 Step 3 — Connect your client

Add the JSON below inside your client config file's `mcpServers` section, replacing `<username>` with your Windows account name.

```json
{
  "mcpServers": {
    "korail-mcp": {
      "command": "C:\\Users\\<username>\\.local\\bin\\korail-mcp.exe"
    }
  }
}
```

> 💡 Not sure of your account name? Run `echo $env:USERNAME` in PowerShell. JSON requires backslashes to be doubled (`\\`).
>
> ⚠️ If you already use other MCP servers, **add only the `korail-mcp` entry** to your existing `mcpServers` block — overwriting the whole file will remove your other servers.

### Config file locations

| Client | Config file |
|---|---|
| **Claude Desktop** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **Claude Code** | registered via `claude mcp add` (see the separate section below) |
| **Cursor** | `C:\Users\<username>\.cursor\mcp.json` |
| **Antigravity** | `C:\Users\<username>\.gemini\antigravity\mcp_config.json` |
| **GitHub Copilot CLI** | registered via `copilot mcp add` (see the separate section below) |
| **VS Code (GitHub Copilot Chat)** | see the separate section below (different JSON format) |

<details>
<summary>Claude Desktop — if the folder doesn't exist</summary>

1. Type `%APPDATA%` in Explorer's address bar and press Enter
2. Create a `Claude` folder if it doesn't exist
3. Inside it, create `claude_desktop_config.json` and paste the JSON above

If `AppData` isn't visible, enable **Hidden items** in Explorer → View.
</details>

<details>
<summary>Claude Code — tested end-to-end with a real account, including an actual tool call</summary>

Tested with the **Claude Code CLI** (`claude`), which runs in a terminal without needing VS Code or Claude Desktop at all.

```powershell
# 1) Register korail-mcp as an MCP server (one-time)
claude mcp add korail-mcp -s user -- "C:\Users\<username>\.local\bin\korail-mcp.exe"

# 2) Ask a real question (only allow that tool)
claude -p "Use the korail-mcp tools to check whether Seoul Station has an elevator" --allowedTools "mcp__korail-mcp__*"
```

> ✅ **Verified 2026-08-24** — ran the commands above for real and got a real-data answer back:
>
> ```
> Seoul Station — has elevators (18)
> Escalators: 23 · Restroom: yes · Nursing room: yes · Info center: yes
> (Source: KORAIL Public Data Portal amenity info, live API)
> ```
>
> Use `claude mcp list` to confirm it's registered, or `claude mcp remove korail-mcp` to remove it. For interactive use, drop `--allowedTools` and Claude Code will ask for approval on the first tool call.
</details>

<details>
<summary>Cursor / Antigravity — if the file or folder doesn't exist</summary>

If the `.cursor` or `.gemini\antigravity` folder (or the config file inside it) doesn't exist yet, just create it yourself.

1. Type `%USERPROFILE%` in Explorer's address bar and press Enter (goes to your account folder)
2. Create the missing folder (`.cursor` or `.gemini\antigravity`)
3. Inside it, create `mcp.json` (Cursor) or `mcp_config.json` (Antigravity) and paste the JSON above

With Antigravity it's even easier to just ask the agent — paste the JSON above into the chat and say "register this MCP server." It can be installed for free; no separate subscription is needed to connect KORAIL MCP.
</details>

<details>
<summary>GitHub Copilot CLI — tested end-to-end with a real account, including an actual tool call</summary>

Tested with the official **GitHub Copilot CLI** (`@github/copilot`), which runs in a terminal without needing VS Code at all. **MCP works on the free plan too.**

> ⚠️ **Prerequisite — Node.js 22 or later.** Check with `node --version`; if missing, install the LTS release from [nodejs.org](https://nodejs.org) (unlike `uv`, this isn't set up automatically).

```powershell
# 1) Install (one-time)
npm install -g @github/copilot

# 2) Register korail-mcp as an MCP server (one-time)
copilot mcp add korail-mcp -- "C:\Users\<username>\.local\bin\korail-mcp.exe"

# 3) Ask a real question (auto-approve tool calls)
copilot -p "Use the korail-mcp tools to check whether Seoul Station has an elevator" --allow-all-tools
```

> ✅ **Verified 2026-08-24** — ran the commands above for real and confirmed GitHub Copilot autonomously called the `get_urban_accessibility` tool and answered from real data:
>
> ```
> ● get_urban_accessibility (MCP: korail-mcp) · station_name: "서울역", facility_type: "elevator"
>
> Yes, Seoul Station has elevators — 17 in total.
> Airport Railroad (AR): 9 · Gyeongui–Jungang Line (KR): 1 · Line 1 (S1): 4 · Line 4 (S1): 3
> ```
>
> The config is written to `~/.copilot/mcp-config.json` under `mcpServers.korail-mcp`. Use `copilot mcp list` to confirm it's registered, or `copilot mcp remove korail-mcp` to remove it.
</details>

<details>
<summary>VS Code (GitHub Copilot Chat) — different JSON format (server protocol tested; VS Code GUI itself not verified)</summary>

The VS Code extension is a separate product from the CLI above, with its own config file. The top-level key is **`servers`**, not `mcpServers`, so you can't reuse the JSON above as-is.

1. Create `.vscode\mcp.json` at the root of your workspace and paste the block below.
   (To make it available in every workspace instead, open the Command Palette (Ctrl+Shift+P) → **MCP: Open User Configuration**, which opens `%APPDATA%\Code\User\mcp.json`.)

```json
{
  "servers": {
    "korail-mcp": {
      "command": "C:\\Users\\<username>\\.local\\bin\\korail-mcp.exe"
    }
  }
}
```

2. Save the file, then click the **Start** button that appears at the top.
3. Open Copilot Chat, switch to **Agent mode**, and check the tools icon — if `korail-mcp`'s 98 tools show up, you're connected.

> ⚠️ **The CLI test above already proves the server side works (stdio protocol, all 98 tools, real data responses) — it does not prove that clicking Start in VS Code actually connects, since this environment has no way to drive the VS Code GUI.** Let us know if it doesn't work.
</details>

### After connecting — fully quit and relaunch your client

> ℹ️ **Not needed for Claude Code or the GitHub Copilot CLI** — they reload config on every run. The steps below only apply to clients that stay open in a window, like Claude Desktop, Cursor, Antigravity, and VS Code.

Closing the window with the X doesn't stop it — it **keeps running in the system tray** (the `^` area near the clock), so the new config won't take effect.
→ Right-click the tray icon → **Quit / Exit**, then relaunch.

Once connected, `korail-mcp` shows as **running** in your client's MCP server list, and all 98 tools become available.

### 💬 Verify it worked — try asking

```
Does Seoul Station have an elevator?
What was the mainline rail transport performance in 2024?
What's the operation plan for KTX train 101?
```

If you get a real answer back, you're all set. More example queries are in the "Example queries" section further down.

---

## 📦 Included Servers (11 servers · 98 tools)

| Server | Tools | Data Provided |
|---|:-:|---|
| m-convenience | 6 | Station amenities, accessibility, elevators, location info |
| m-stats | 15 | Passenger/freight transport stats, ticketing stats, usage type, KTX long-term stats |
| m-train-ops | 4 | Train operation plans and history |
| m-codebook | 4 | Station/route code lookup |
| m-freight | 11 | Freight, containers, logistics facilities, items, hazardous cargo |
| m-network | 8 | Routes, inter-station distance, fares, station track specs |
| m-rolling-stock | 6 | Rolling stock inventory, model specs, operation records by type |
| m-voc-cs | 10 | Customer service, information disclosure |
| m-internal-svc | 14 | Leased stores, social contribution, HR info |
| m-procurement | 4 | Material groups, G2B item names, material attributes, target equipment |
| m-urban-rail | 16 | Nationwide urban rail stations, routes, rolling stock facilities, accessibility, safety, environment, timetables |

### Tool details per server (click to expand)

<details>
<summary><b>m-convenience</b> · 6 tools — Station amenities</summary>

| Tool | Description |
|---|---|
| get_station_facilities | Look up station amenities by station name |
| get_accessible_facilities | Look up accessibility facilities by station name |
| list_stations_with_elevator | List stations with elevators |
| get_station_facilities_detail | Interior/exterior facility status by station |
| get_station_transfer_info | Transfer info to other transit modes by station |
| get_station_location | Station location (coordinates) |
</details>

<details>
<summary><b>m-stats</b> · 15 tools — Passenger/freight transport statistics</summary>

| Tool | Description |
|---|---|
| get_mainline_station_per | Mainline boarding/alighting stats by station |
| get_mainline_route_per | Mainline ridership stats by route |
| get_wide_rail_station_per | Metropolitan rail boarding/alighting stats by station |
| get_wide_rail_route_per | Metropolitan rail ridership stats by route |
| get_mainline_distance_per | Mainline ridership stats by distance band |
| get_mainline_model_per | Mainline ridership stats by train model |
| get_mainline_day_of_week_per | Mainline ridership stats by day of week |
| get_mainline_grade_per | Mainline ridership stats by seat class |
| get_mainline_ticketing_stat | Mainline ticketing-type statistics |
| get_mainline_person_distance | Mainline passenger-distance stats by route |
| get_ktx_long_term_stats | KTX long-term statistics |
| get_mainline_carriage | Mainline passenger train carriage/traffic performance |
| get_wide_area_carriage | Metropolitan passenger train carriage/traffic performance |
| get_freight_carriage | Freight train carriage/traffic performance |
| get_transport_stat_codes | Transport performance statistics code info |
</details>

<details>
<summary><b>m-train-ops</b> · 4 tools — Train operations</summary>

| Tool | Description |
|---|---|
| get_train_codes | Train operation code info |
| get_train_run_plan | Passenger train operation plan |
| get_train_run_info | Passenger train real-time operation info |
| get_train_run_history | Next-gen ticketing system train run history |
</details>

<details>
<summary><b>m-codebook</b> · 4 tools — Station/route codes</summary>

| Tool | Description |
|---|---|
| search_station | Look up station code, English name, and regional HQ by station name |
| decode_station_code | Look up station name by station code |
| search_route | Look up route code by route name |
| list_stations_by_region | List stations under a regional headquarters |
</details>

<details>
<summary><b>m-freight</b> · 11 tools — Freight & logistics</summary>

| Tool | Description |
|---|---|
| search_freight_code | Search internal freight codes |
| decode_freight_code | Decode a single internal freight classification code |
| search_container_record | Look up container loading history |
| list_freight_work_lines | Freight loading/unloading work-line info |
| list_standard_loading_time | Standard loading-time master lookup |
| search_loading_time_adjustment | Look up loading-time adjustment history |
| search_consignment_change | Search consignment-change fees |
| search_consignment_change_per_wagon | Consignment-change fees by wagon |
| get_logistics_facility | Integrated logistics facility info |
| get_freight_items | Freight item info |
| get_hazardous_cargo | Hazardous cargo info |
</details>

<details>
<summary><b>m-network</b> · 8 tools — Routes, distance, fares</summary>

| Tool | Description |
|---|---|
| search_operation_patterns | Search nationwide rail operation patterns |
| get_station_distance | Shortest operating distance between two stations |
| get_freight_minimum_fare | Freight minimum-fare standards |
| get_freight_rate | Rail freight rate info |
| get_segment_info | EMU segment info |
| get_operation_distance | Inter-station operating distance by route |
| get_ktx_stations | KTX stations by route |
| get_station_track_info | Detailed track/facility info by station |
</details>

<details>
<summary><b>m-rolling-stock</b> · 6 tools — Rolling stock</summary>

| Tool | Description |
|---|---|
| get_train_type_specs | Locomotive/EMU model specifications |
| get_rolling_stock_by_year | Rolling stock inventory by year |
| get_wagon_by_weight_class | Freight wagon inventory by tare-weight class |
| get_wagon_by_load_capacity | Freight wagon inventory by load capacity |
| get_maintenance_equipment | Rolling-stock maintenance equipment inventory |
| get_train_operation_by_type | Annual operation performance by train type |
</details>

<details>
<summary><b>m-voc-cs</b> · 10 tools — Customer service & disclosure</summary>

| Tool | Description |
|---|---|
| get_customer_satisfaction_stats | Daily customer-satisfaction statistics |
| get_consultation_types | Customer center consultation-type codes |
| get_consultation_departments | Customer center department directory |
| get_advance_disclosure | Advance information-disclosure list |
| get_advance_disclosure_detail | Advance information-disclosure details |
| get_advance_disclosure_files | Advance information-disclosure attachments |
| get_info_disclosure_dept | Information-disclosure department directory |
| get_info_disclosure_codes | Information-disclosure system common codes |
| get_homepage_dept | KORAIL website department info |
| get_homepage_position | KORAIL website position codes |
</details>

<details>
<summary><b>m-internal-svc</b> · 14 tools — Leasing, social contribution, HR</summary>

| Tool | Description |
|---|---|
| get_lease_stores | In-station leased store operating info |
| get_lease_codes | Lease system codes |
| get_leased_assets | Leased asset status |
| get_dormitory_longterm_codes | Employee dormitory long-term reservation reason codes |
| get_social_funds | Social contribution fund types |
| get_social_volunteer_fields | Social contribution volunteer field codes |
| get_social_donations | Charity fund usage records |
| get_social_volunteer_matching | Volunteer-activity matching expenditure records |
| get_social_org | Social contribution portal organization info |
| get_support_facilities | Head office building support facilities |
| get_support_departments | Support department staffing status |
| get_office_meeting_rooms | Head office meeting room list |
| get_job_grades | Job grade code info |
| get_cafeteria_menu_stats | Cafeteria menu count statistics |
</details>

<details>
<summary><b>m-procurement</b> · 4 tools — Procurement & materials</summary>

| Tool | Description |
|---|---|
| search_material_group | Search material group codes |
| search_g2b_item | Search G2B classification numbers/item names |
| search_material_attr | Material attribute info |
| search_material_equipment | Material target equipment info |
</details>

<details>
<summary><b>m-urban-rail</b> · 16 tools — Nationwide urban rail stations, routes, rolling stock (Korea Rail Network Authority)</summary>

> Covers Seoul-area subway lines 1–9, Sinbundang Line, Airport Railroad, plus Busan, Daegu, Daejeon, Gwangju, Incheon, light rail, GTX, and more — 1,108 stations across 22 operators nationwide.
> Requires operator/line/station codes, so use `search_urban_station` first to identify the station. Same-named transfer stations are distinguished by `operator`.

| Tool | Description |
|---|---|
| search_urban_station | Search operator/line/station code by station name (precedes other lookups) |
| get_urban_station_info | Station basic info (address, coordinates, multilingual names) |
| get_urban_accessibility | Station accessibility facilities (elevators/escalators/wheelchair lifts — status, location, routing, safety plates, gap distance, braille, accessible restrooms, adjacent-stair car numbers, etc.) |
| get_urban_amenity | Station amenities (restrooms, nursing rooms, lockers, ATMs, lost & found, Wi-Fi) |
| get_urban_safety | Station safety facilities (defibrillators, fire equipment, emergency call phones, air respirators, screen doors, platform safety fences) |
| get_urban_surroundings | Facilities around the station (public transit, parking, bike parking/rental) |
| get_urban_exit_info | Station exit info (exit numbers, nearby facilities, distance) |
| get_urban_transfer_info | Station transfer info (transfer lines, distance, routing) |
| get_urban_movement | Barrier-free routing from entrance to platform for reduced-mobility users |
| get_urban_platform | Station platform info (platform type, whether combined, etc.) |
| get_urban_environment | Station environmental measurements (air quality, temperature, humidity, noise) |
| get_urban_timetable | Station-specific timetable (weekday/holiday, express option) |
| get_urban_route | Full station composition of a route (up/down order) — station-independent |
| get_urban_train_composition | Train formation types by operator (formation code, car number) — precedes per-car lookups |
| get_urban_train_facility | Per-car facilities (fire extinguishers, emergency call phones, defibrillators, priority seating, wheelchair space, etc.) |
| get_urban_train_environment | In-train environmental info per car (temperature, humidity, fine dust, etc.) |
</details>

---

## 🧩 Other setups

<details>
<summary>ChatGPT · Grok — require a remote connection</summary>

ChatGPT and Grok **don't support local MCP servers.** They only accept a public HTTPS endpoint as a connector, so the setup above won't work for them.

The gateway includes a built-in remote (Streamable HTTP) mode, so connecting is possible **if you expose a public address.** This comes with hosting and exposure considerations — see [gateway/README.md](gateway/README.md) for details.
</details>

<details>
<summary>Running via uvx without installing — not recommended</summary>

You can also run it directly with `uvx`, with no install step.

```json
{
  "mcpServers": {
    "korail-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/lovelyquality/korail-mcp.git", "korail-mcp"]
    }
  }
}
```

This avoids needing your account name, but **it checks GitHub for the latest commit on every launch**, so your client starts slower every time.

| Method | Startup time (measured) |
|---|---|
| Run after `uv tool install` | **~5 seconds** |
| `uvx` (checks remote every time) | ~40 seconds |

If startup is too slow, your client may time out waiting for the server and the tools won't appear.
</details>

<details>
<summary>For developers — running from a cloned repo</summary>

To modify the server code, clone the repository and run it directly.

```bash
git clone https://github.com/lovelyquality/korail-mcp.git
cd korail-mcp
uv run gateway/server.py
```

Dependencies are declared at the top of `gateway/server.py`, so `uv` prepares them automatically. After making changes, run
`python docker-test/smoke_test.py` to verify all 11 servers, 98 tools, and their return-type declarations at once.

See [gateway/README.md](gateway/README.md) for details.
</details>

---

## 💬 Example queries

```
Does Seoul Station have an elevator?                        (convenience)
What was the KTX ticketing-type ratio for April 2026?        (stats)
What's the operation plan for KTX train 101?                 (train-ops)
What's the station code for Seoul Station?                   (codebook)
What was the mainline rail transport performance in 2024?    (stats)
Look up the container freight shipping history.               (freight)
Show me the Gyeongbu Line KTX stops and inter-station distances. (network)
Show me the KTX rolling stock model specifications.           (rolling-stock)
What are the customer center consultation type codes?         (voc-cs)
What's the leased store status at station buildings?          (internal-svc)
Search the material group code for "EMU supplies".            (procurement)
Where are the elevators at Gangnam Station (Seoul Metro)?     (urban-rail)
Find the operators for the urban rail stations at Seoul Station. (urban-rail)
```

---

## 📚 Data sources

- KORAIL Public Data Portal ([data.go.kr](https://www.data.go.kr))
- Korea Rail Network Authority (KRIC) Railway Industry Information Center Open API ([openapi.kric.go.kr](https://openapi.kric.go.kr)) — urban rail station info
- REST API (B551457) · odcloud file-conversion API · local CSV

## ⚠️ Notes

- All data calls go through a dedicated **Cloudflare Workers proxy**, so no personal API key is required.
- Each dataset's reference date and update cycle appears in the `_meta` field of the tool's response.

---

For details on each server's behavior, see the `server.py` docstring in the corresponding folder.
