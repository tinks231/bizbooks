# 🧪 Test File Upload Locally

## Why Test Locally?
- See logs immediately in terminal
- No need to wait for Vercel deployment
- Easier to debug

## Steps:

### 1. Start Local Server
```bash
cd /Users/rishjain/Downloads/attendence_app/modular_app
source ../venv/bin/activate
export FLASK_APP=app.py
export FLASK_ENV=development
export DATABASE_URL="your_supabase_url"
export BLOB_READ_WRITE_TOKEN="your_blob_token"
flask run --port 5001
```

### 2. Access via ngrok (if needed)
```bash
ngrok http 5001
```

### 3. Test Purchase Request
- Go to employee portal
- Submit purchase request with image
- **Watch terminal for logs:**
  - 📎 Checking for document upload...
  - 📎 Files in request: [...]
  - 📤 Starting upload...
  - etc.

### 4. Check Output
You'll see EXACTLY where it fails!

## Expected Output:

**Success:**
```
📎 Checking for document upload...
📎 Files in request: ['document']
📎 File object: <FileStorage: 'photo.jpg' ('image/jpeg')>
📎 Filename: photo.jpg
📤 Starting upload for: photo.jpg
📐 Resized image to 1600x1200
🗜️ Compressed: 8.50MB → 1.20MB (saved 86%)
✅ Document uploaded: photo.jpg → https://blob-url...
```

**Failure (example):**
```
📎 Checking for document upload...
📎 Files in request: []  ← EMPTY! No file received!
📎 No document in request.files
```

This will tell us EXACTLY what's wrong!
