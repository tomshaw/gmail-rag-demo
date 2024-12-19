# Gmail RAG Demo

This script allows you to access emails from your Gmail account using the Gmail API.

## Setup

1. **Install Dependencies**
   ```bash
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

2. **Google Cloud Console Setup**
   1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
   2. Create a new project or select an existing one
   3. Enable the Gmail API:
      - In the sidebar, navigate to "APIs & Services" > "Library"
      - Search for "Gmail API"
      - Click "Enable"
   4. Configure OAuth Consent Screen:
      - Go to "APIs & Services" > "OAuth consent screen"
      - Select "External" user type
      - Fill in the required application information
      - Add the scope: `.../auth/gmail.readonly`
      - Add your email as a test user
   5. Create Credentials:
      - Go to "APIs & Services" > "Credentials"
      - Click "Create Credentials" > "OAuth client ID"
      - Choose "Desktop application"
      - Download the JSON file and rename it to `credentials.json`
      - Place `credentials.json` in your project root directory

## Usage

1. Run the script with optional arguments:
   ```bash
   # Default usage (fetches 10 emails from INBOX)
   python app.py

   # Specify a different label
   python app.py --label="SENT"

   # Specify number of emails to fetch
   python app.py --limit=25

   # Specify both label and limit
   python app.py --label="SENT" --limit=25
   ```

2. Working with Gmail subfolders/nested labels:
   - Use forward slashes (/) or escaped backslashes (\\) for nested labels
   ```bash
   # These are equivalent:
   python app.py --label="Parent/Subfolder"
   python app.py --label="Parent\\Subfolder"

   # Examples:
   python app.py --label="Work/Projects"
   python app.py --label="Personal/Receipts"
   ```

## Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--label` | Gmail label to fetch emails from | `INBOX` |
| `--limit` | Maximum number of emails to fetch | `10` |

## Features

- Authenticates with Gmail API
- Retrieves emails from specified Gmail label (default: INBOX)
- Displays email snippets

## Security Notes

- Keep `credentials.json` and `token.json` secure and never commit them to version control
- The included `.gitignore` file will help prevent accidentally committing these files

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

