# 🔑 GitHub Token Setup Guide

The MCP server now supports GitHub authentication to avoid rate limits!

## 🚀 Quick Setup (2 minutes)

### Step 1: Create GitHub Personal Access Token

1. **Go to GitHub Settings**
   - Visit: https://github.com/settings/tokens
   - Or: GitHub.com → Profile (top right) → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token (Classic)**
   - Click "Generate new token" → "Generate new token (classic)"
   - Note: Give it a descriptive name like "MCP Server - Hackathon"

3. **Set Token Permissions**
   - **NO permissions needed!** (Just read public repos)
   - Expiration: 7 days (enough for hackathon)
   - Leave all checkboxes UNCHECKED (we only need public repo access)
   - Scroll to bottom, click "Generate token"

4. **Copy the Token**
   - Copy the token that starts with `ghp_...`
   - ⚠️ **Save it somewhere** - you won't see it again!

### Step 2: Set Environment Variable

**On Windows (PowerShell):**
```powershell
# Temporary (current session only)
$env:GITHUB_TOKEN="ghp_your_token_here"

# Permanent (all sessions)
[System.Environment]::SetEnvironmentVariable('GITHUB_TOKEN', 'ghp_your_token_here', 'User')
```

**On Windows (Command Prompt):**
```cmd
set GITHUB_TOKEN=ghp_your_token_here
```

**On Mac/Linux:**
```bash
export GITHUB_TOKEN="ghp_your_token_here"

# To make permanent, add to ~/.bashrc or ~/.zshrc:
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Verify It Works

```bash
# Test the demo script
python demo.py

# Or test with Codex
codex exec --skip-git-repo-check "Analyze the facebook/react repository"
```

**You should now get:**
- ✅ No rate limit errors
- ✅ 5,000 requests/hour (instead of 60)
- ✅ Faster responses

---

## 🔐 Security Notes

**Is this safe?**
- ✅ Yes! The token has NO permissions (read-only for public repos)
- ✅ Token is stored locally on your machine
- ✅ Not committed to git (in .gitignore)
- ✅ Expires in 7 days automatically

**Best practices:**
- Don't commit the token to GitHub
- Don't share the token publicly
- Delete token after hackathon if not needed

---

## 🧪 Testing Without Token

**If you can't/don't want to set up a token:**

1. **Wait between API calls** (rate limit resets every hour)
2. **Use the demo with fewer repos** (test with just 1-2 repos)
3. **Show the code in your video** instead of live demo

**For hackathon video:**
- You can record the demo.py output (works without token for 1-2 repos)
- Or show the code and explain how it works
- Or use screenshots of successful runs

---

## ❓ Troubleshooting

**"Error: GitHub API rate limit exceeded"**
- Set up GitHub token (see above)
- OR wait 1 hour for rate limit reset
- OR use fewer API calls in demo

**Token not working?**
- Restart terminal/PowerShell after setting environment variable
- Verify with: `echo $env:GITHUB_TOKEN` (Windows) or `echo $GITHUB_TOKEN` (Mac/Linux)
- Make sure token starts with `ghp_`

**Still getting rate limited?**
- Check token is set correctly: Run Python and check `import os; print(os.environ.get('GITHUB_TOKEN'))`
- Token might be expired (regenerate)
- Multiple programs using same token (each has separate limit)

---

## 📊 Rate Limits

| Auth Type | Limit | Use Case |
|-----------|-------|----------|
| No token | 60/hour | Quick testing only |
| With token | 5,000/hour | Full demo, development |

**For hackathon:** Token is highly recommended but not required if you limit testing.

---

## 🎥 Demo Video Without Token

**If you can't set up token before deadline:**

1. **Record screenshots** instead of live demo
2. **Show the code** and explain the logic
3. **Use 1-2 test repos** (stays within 60/hour limit)
4. **Mention in video**: "Token auth supported for production use"

**Sample script:**
"The MCP server supports GitHub authentication for unlimited API access. For this demo, I'll use public API with a few test repositories..."

---

## ✅ Quick Checklist

- [ ] Created GitHub personal access token
- [ ] Set GITHUB_TOKEN environment variable
- [ ] Verified with `python demo.py`
- [ ] Token works with Codex
- [ ] Ready for submission!

---

**Need help?** This is optional for hackathon - the server works without token for limited testing!
