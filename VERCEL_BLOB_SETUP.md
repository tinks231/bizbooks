# Vercel Blob Storage Setup Guide

## Why Vercel Blob?

Your attendance photos were too large to store in the database (1.6MB+ each as base64). 

**Solution:** Vercel Blob Storage (Free Tier)
- ✅ **Free:** 1GB storage, 100GB bandwidth/month
- ✅ **Fast:** Global CDN for photo delivery
- ✅ **Reliable:** No database bloat

---

## Setup Steps (5 minutes)

### Step 1: Create Vercel Blob Store

1. Go to your Vercel project dashboard: https://vercel.com/dashboard
2. Click on your project (`bizbooks-dun`)
3. Go to **Storage** tab
4. Click **Create Database** → **Blob**
5. Name it: `bizbooks-photos`
6. Click **Create**

### Step 2: Get the Blob Token

After creating the Blob store:

1. Vercel will show you the **environment variables**
2. Copy the `BLOB_READ_WRITE_TOKEN` value
3. It looks like: `vercel_blob_rw_aBcD1234_xYz567890...`

### Step 3: Add to Vercel Environment Variables

1. Go to **Settings** → **Environment Variables** in your Vercel project
2. Click **Add New**
3. Set:
   - **Name:** `BLOB_READ_WRITE_TOKEN`
   - **Value:** (paste the token you copied)
   - **Environment:** Check all (Production, Preview, Development)
4. Click **Save**

### Step 4: Redeploy

Go to **Deployments** tab and click **Redeploy** on the latest deployment.

---

## How It Works Now

### For Vercel (Production):
```
Employee takes photo → Uploaded to Vercel Blob Storage → URL saved in database
Example: https://blob.vercel-storage.com/attendance/rishi_jain_20250125.jpg
```

### For Local Development:
```
Employee takes photo → Saved to local uploads/ folder → Filename saved in database
Example: rishi_jain_20250125.jpg
```

---

## Database Changes

✅ Changed column types:
- `attendance.photo`: `VARCHAR(200)` → `TEXT` (to store long URLs)
- `employees.document_path`: `VARCHAR(200)` → `TEXT` (to store long URLs)

⚠️ **Note:** Supabase will automatically apply these changes when you redeploy.

---

## Verify It's Working

After redeploying:

1. Register a test client: https://bizbooks.co.in/register
2. Create subdomain: `test123`
3. Add an employee
4. Mark attendance with photo
5. Check admin dashboard - photo should display

If photo appears, ✅ Vercel Blob is working!

---

## Free Tier Limits

**Vercel Blob Free Tier:**
- Storage: 1 GB
- Bandwidth: 100 GB/month

**Estimated capacity:**
- Average photo: ~300 KB
- **~3,000 photos per GB**
- With 3 clients, 10 employees each, 2 photos/day:
  - 60 photos/day = 18 MB/day
  - **1 GB = ~55 days of photos**

For production, consider:
1. Cloudflare R2 (10 GB free)
2. AWS S3 (5 GB free for 12 months)
3. Photo compression (reduce file size by 50-70%)

---

## Troubleshooting

### "BLOB_READ_WRITE_TOKEN not found"
- Verify environment variable is set in Vercel
- Redeploy after adding the variable

### "Photo upload failed"
- Check Vercel logs for errors
- Verify Blob store is created
- Ensure token has read/write permissions

### Photos not displaying
- Check browser console for errors
- Verify photo URL is a valid HTTPS link
- Check CORS settings (Vercel Blob enables by default)

---

## Next Steps

After Vercel Blob is working:

1. ✅ Test with real clients
2. ✅ Monitor storage usage in Vercel dashboard
3. 🔄 Consider adding photo compression later (optional)

**Your app is now production-ready! 🚀**

