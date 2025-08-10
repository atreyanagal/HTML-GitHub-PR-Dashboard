from flask import Flask, request, jsonify
import requests
from urllib.parse import urlparse

app = Flask(__name__)
GITHUB_TOKEN = "YOUR_GITHUB_PAT"  # Replace with SSO-enabled PAT

def github_api(url):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    return requests.get(url, headers=headers)

def get_pr_status(pr_url):
    try:
        path_parts = urlparse(pr_url).path.strip("/").split("/")
        owner, repo, _, pr_number = path_parts
    except ValueError:
        return {"url": pr_url, "status": "Invalid URL"}

    pr_resp = github_api(f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}")
    if pr_resp.status_code != 200:
        return {"url": pr_url, "status": f"Error: {pr_resp.status_code}"}
    pr_data = pr_resp.json()

    state = pr_data["state"]
    merged = pr_data["merged"]
    draft = pr_data.get("draft", False)
    mergeable_state = pr_data.get("mergeable_state", "unknown")
    head_sha = pr_data["head"]["sha"]
    author = pr_data["user"]["login"]
    from_branch = pr_data["head"]["ref"]
    to_branch = pr_data["base"]["ref"]
    merged_by = pr_data["merged_by"]["login"] if merged and pr_data.get("merged_by") else ""

    # Status mapping
    if state == "open" and draft:
        pr_status = "Draft"
    elif state == "open":
        pr_status = "Open"
    elif state == "closed" and merged:
        pr_status = "Merged"
    elif state == "closed":
        pr_status = "Closed without merge"
    else:
        pr_status = "Unknown"

    # Conflicts & Out of date status
    if mergeable_state == "clean":
        conflict_status = "No conflicts"
        out_of_date = "No"
    elif mergeable_state == "dirty":
        conflict_status = ⚠️ Has conflicts"
        out_of_date = "No"
    elif mergeable_state == "behind":
        conflict_status = "No conflicts"
        out_of_date = "✅ Out of date"
    elif mergeable_state == "blocked":
        conflict_status = "Blocked (checks/reviews)"
        out_of_date = "No"
    else:
        conflict_status = f"Unknown ({mergeable_state})"
        out_of_date = "Unknown"

    # CI details
    checks_resp = github_api(f"https://api.github.com/repos/{owner}/{repo}/commits/{head_sha}/check-runs")
    check_runs = []
    if checks_resp.status_code == 200:
        for run in checks_resp.json().get("check_runs", []):
            check_runs.append(f"{'✅' if run['conclusion'] == 'success' else '❌' if run['conclusion'] == 'failure' else '⏳'} {run['name']}")
    else:
        check_runs.append("❔ No check runs found")

    # Reviews info
    reviews_resp = github_api(f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews")
    approvals = 0
    change_requests = 0
    if reviews_resp.status_code == 200:
        seen_users = {}
        for review in reviews_resp.json():
            seen_users[review["user"]["login"]] = review["state"]
        for state_val in seen_users.values():
            if state_val == "APPROVED":
                approvals += 1
            elif state_val == "CHANGES_REQUESTED":
                change_requests += 1

    return {
        "url": pr_url,
        "status": pr_status,
        "author": author,
        "merged_by": merged_by,
        "from_branch": from_branch,
        "to_branch": to_branch,
        "ci_details": check_runs,
        "conflicts": conflict_status,
        "out_of_date": out_of_date,
        "approvals": approvals,
        "change_requests": change_requests
    }

@app.route("/", methods=["GET"])
def index():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>PR Status Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #121212; color: #e0e0e0; }
        textarea, select { background: #1e1e1e; color: #fff; border: 1px solid #333; padding: 10px; border-radius: 5px; }
        textarea { width: 100%; height: 100px; }
        button { padding: 10px 20px; margin-top: 10px; background-color: #6200ea; color: white; border: none; cursor: pointer; border-radius: 5px; }
        button:hover { background-color: #3700b3; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #333; padding: 8px; text-align: left; }
        th { background-color: #1f1f1f; }
        tr:nth-child(even) { background-color: #1a1a1a; }
        .ci-details { font-size: 0.9em; color: #bbb; }
        #searchBox, #statusFilter { margin-top: 20px; padding: 8px; }
        .status-open   { color: #4caf50; font-weight: bold; }
        .status-merged { color: #9c27b0; font-weight: bold; }
        .status-closed { color: #f44336; font-weight: bold; }
        .status-draft  { color: #9e9e9e; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🚀 PR Status Dashboard</h1>
    <textarea id="prLinks" placeholder="Paste one PR link per line"></textarea><br>
    <button onclick="checkPRs()">Check Status</button>

    <div style="margin-top:15px;">
        <input type="text" id="searchBox" placeholder="Search by author..." onkeyup="applyFilters()">
        <select id="statusFilter" onchange="applyFilters()">
            <option value="">All Statuses</option>
            <option value="Open">Open</option>
            <option value="Merged">Merged</option>
            <option value="Closed without merge">Closed without merge</option>
            <option value="Draft">Draft</option>
        </select>
    </div>

    <table id="resultsTable" style="display:none;">
        <thead>
            <tr>
                <th>PR Link</th>
                <th>Author</th>
                <th>Status</th>
                <th>Merged By</th>
                <th>From → To</th>
                <th>CI Details</th>
                <th>Conflicts</th>
                <th>Out of Date</th>
                <th>Approvals</th>
                <th>Change Requests</th>
            </tr>
        </thead>
        <tbody></tbody>
    </table>

    <script>
        async function checkPRs() {
            const links = document.getElementById("prLinks").value.split("\\n");
            const res = await fetch("/check", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({links})
            });
            const data = await res.json();

            const table = document.getElementById("resultsTable");
            const tbody = table.querySelector("tbody");
            tbody.innerHTML = "";

            data.forEach(item => {
                const details = item.ci_details.join("<br>");
                let statusClass = "";
                if (item.status === "Open") statusClass = "status-open";
                else if (item.status === "Merged") statusClass = "status-merged";
                else if (item.status === "Closed without merge") statusClass = "status-closed";
                else if (item.status === "Draft") statusClass = "status-draft";

                const row = `<tr class="${statusClass}">
                    <td><a href="${item.url}" target="_blank" style="color:#82b1ff;">${item.url}</a></td>
                    <td>${item.author}</td>
                    <td class="${statusClass}">${item.status}</td>
                    <td>${item.merged_by || "-"}</td>
                    <td>${item.from_branch} → ${item.to_branch}</td>
                    <td class="ci-details">${details}</td>
                    <td>${item.conflicts}</td>
                    <td>${item.out_of_date}</td>
                    <td>${item.approvals}</td>
                    <td>${item.change_requests}</td>
                </tr>`;
                tbody.innerHTML += row;
            });

            table.style.display = "table";
        }

        function applyFilters() {
            const authorFilter = document.getElementById("searchBox").value.toLowerCase();
            const statusFilter = document.getElementById("statusFilter").value;
            const table = document.getElementById("resultsTable");
            const trs = table.getElementsByTagName("tr");

            for (let i = 1; i < trs.length; i++) {
                const authorCell = trs[i].getElementsByTagName("td")[1];
                const statusCell = trs[i].getElementsByTagName("td")[2];
                if (authorCell && statusCell) {
                    const matchesAuthor = authorCell.textContent.toLowerCase().includes(authorFilter);
                    const matchesStatus = statusFilter === "" || statusCell.textContent === statusFilter;
                    trs[i].style.display = matchesAuthor && matchesStatus ? "" : "none";
                }
            }
        }
    </script>
</body>
</html>
"""

@app.route("/check", methods=["POST"])
def check():
    pr_links = request.json.get("links", [])
    results = [get_pr_status(link.strip()) for link in pr_links if link.strip()]
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
