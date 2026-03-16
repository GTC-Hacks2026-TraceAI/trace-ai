#!/usr/bin/env bash
# =============================================================================
# Trace AI — end-to-end demo script
#
# Walks through the full investigation flow:
#   1. Health check
#   2. Create a missing-person case
#   3. Run vision search (scores all indexed frames)
#   4. Build the movement timeline
#   5. Get camera recommendations for the next step
#
# Prerequisites
#   • The Trace AI server must already be running:
#       python -m uvicorn app.main:app --reload
#   • curl and python (for pretty-printing JSON) must be installed.
#
# Usage
#   bash scripts/demo.sh [BASE_URL]
#
# Examples
#   bash scripts/demo.sh
#   bash scripts/demo.sh http://127.0.0.1:8000
# =============================================================================

set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8000}"

# ── Helpers ────────────────────────────────────────────────────────────────────

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RESET='\033[0m'

header() {
  echo ""
  echo -e "${CYAN}=== $* ===${RESET}"
}

json_field() {
  # Usage: json_field <json_string> <field_name>
  echo "$1" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('$2',''))"
}

pp() {
  python -m json.tool
}

# ── Step 0: health check ───────────────────────────────────────────────────────

header "STEP 0 — Health check"
HEALTH=$(curl -sf "${BASE_URL}/health")
echo "${HEALTH}" | pp
STATUS=$(json_field "${HEALTH}" "status")
if [[ "${STATUS}" != "ok" ]]; then
  echo -e "${YELLOW}Server does not appear to be running at ${BASE_URL}. Exiting.${RESET}"
  exit 1
fi

# ── Step 1: create a case ──────────────────────────────────────────────────────

header "STEP 1 — Create missing-person case"
CASE_JSON=$(curl -sf -X POST "${BASE_URL}/cases" \
  -H "Content-Type: application/json" \
  -d '{
        "subject_name":          "Alex Johnson",
        "description":           "Adult, medium build, brown hair",
        "last_known_location":   "North Campus Main Entrance",
        "clothing":              "blue hoodie backpack"
      }')
echo "${CASE_JSON}" | pp

CASE_ID=$(json_field "${CASE_JSON}" "id")
SUBJECT=$(json_field "${CASE_JSON}" "subject_name")
echo -e "${GREEN}Created case ${CASE_ID}  (subject: ${SUBJECT})${RESET}"

# ── Step 2: run vision search ──────────────────────────────────────────────────

header "STEP 2 — Run vision search  (scores all indexed frames)"
SEARCH_JSON=$(curl -sf -X POST "${BASE_URL}/cases/${CASE_ID}/search")
echo "${SEARCH_JSON}" | pp

# Show summary of top result
TOP_CAMERA=$(echo "${SEARCH_JSON}" | python -c "
import sys, json
sightings = json.load(sys.stdin)
if sightings:
    s = sightings[0]
    print(f\"Top sighting → camera {s['camera_id']}  |  score {s['similarity_score']:.3f}\")
    print(f\"  {s['explanation']}\")
else:
    print('No sightings returned.')
")
echo -e "${GREEN}${TOP_CAMERA}${RESET}"

# ── Step 3: build movement timeline ───────────────────────────────────────────

header "STEP 3 — Build movement timeline"
TIMELINE_JSON=$(curl -sf "${BASE_URL}/cases/${CASE_ID}/timeline")
echo "${TIMELINE_JSON}" | pp

SUMMARY=$(json_field "${TIMELINE_JSON}" "summary")
echo -e "${GREEN}Summary: ${SUMMARY}${RESET}"

# ── Step 4: get camera recommendations ────────────────────────────────────────

header "STEP 4 — Camera recommendations  (next cameras to inspect)"
RECS_JSON=$(curl -sf "${BASE_URL}/cases/${CASE_ID}/recommendations")
echo "${RECS_JSON}" | pp

echo ""
echo "${RECS_JSON}" | python -c "
import sys, json
recs = json.load(sys.stdin)
if not recs:
    print('No recommendations returned.')
else:
    for r in recs:
        urgency  = r.get('urgency_level') or 'n/a'
        deadline = r.get('review_before')  or ''
        deadline_str = f'  review before {deadline}' if deadline else ''
        print(f\"  #{r['priority']}  {r['camera_id']} — {r['camera_name']}  \"\
              f\"({r['location']})  urgency={urgency}{deadline_str}\")
        print(f\"      reason: {r['reason']}\")
"

# ── Done ───────────────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}Demo complete.${RESET}"
echo "  Case ID  : ${CASE_ID}"
echo "  Subject  : ${SUBJECT}"
echo "  Docs     : ${BASE_URL}/docs"
