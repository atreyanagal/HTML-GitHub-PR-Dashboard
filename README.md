Here’s a **README.md** you can use for your GitHub repository containing the above Flask-based PR Status Dashboard:

---

````markdown
# 🚀 GitHub PR Status Dashboard

A lightweight **Flask** web application that allows you to check the status of multiple GitHub Pull Requests at once.  
It fetches details like **status, author, merged by, branches, CI check runs, conflicts, out-of-date status, approvals, and change requests**—all in a clean, searchable dashboard.

---

## 📌 Features
- ✅ Check multiple PRs at once (paste PR links in textarea)  
- ✅ View **status**: Open, Draft, Merged, Closed without merge  
- ✅ See **author** and **merged by** details  
- ✅ Shows **from → to** branch information  
- ✅ Displays **CI check run** results (✅, ❌, ⏳)  
- ✅ Detects **conflicts** and **out-of-date branches**  
- ✅ Shows **approvals** and **change requests** from reviews  
- ✅ Search by **author** and filter by **status**  
- ✅ Dark mode UI with color-coded statuses  

---

## 🖼 Demo Screenshot
![Demo](docs/demo.png)  
*(Optional — Add a screenshot after running the app)*

---

## ⚙️ Installation & Setup

### 1️⃣ Clone this repository
```bash
git clone https://github.com/yourusername/pr-status-dashboard.git
cd pr-status-dashboard
````

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # For Mac/Linux
venv\Scripts\activate      # For Windows
```

### 3️⃣ Install dependencies

```bash
pip install flask requests
```

### 4️⃣ Set your GitHub Token

Edit `app.py` and replace:

```python
GITHUB_TOKEN = "YOUR_GITHUB_PAT"  # Replace with SSO-enabled PAT
```

> **Note:** Use a **Personal Access Token (PAT)** with `repo` scope (and SSO enabled if required).
> [GitHub Token Guide](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)

### 5️⃣ Run the app

```bash
python app.py
```

Open the app in your browser:

```
http://127.0.0.1:5000
```

---

## 📋 How to Use

1. Paste one or more GitHub PR URLs in the textarea
2. Click **Check Status**
3. View PR details in the table
4. Use the search box to filter by **author**
5. Use the dropdown to filter by **status**

---

## 🎨 UI Color Codes

| Status               | Color     |
| -------------------- | --------- |
| Open                 | 🟢 Green  |
| Merged               | 🟣 Purple |
| Closed without merge | 🔴 Red    |
| Draft                | ⚪ Grey    |

---

## 📌 Example

**Input:**

```
https://github.com/octocat/Hello-World/pull/1347
https://github.com/yourorg/yourrepo/pull/25
```

**Output:**
A table showing each PR's status, CI results, conflicts, branches, approvals, and more.

---

## 🛠 Technologies Used

* **Python 3**
* **Flask** – Web framework
* **Requests** – GitHub API calls
* **HTML, CSS, JavaScript** – Frontend dashboard

---

## 📜 License

This project is licensed under the MIT License. You are free to use, modify, and distribute it.

---

## 🤝 Contributions

Pull requests are welcome!
If you find a bug or want a new feature, open an issue.

```
