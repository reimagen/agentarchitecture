# Vercel Deployment Guide

Your frontend is now configured and ready for Vercel deployment. Follow these steps to deploy:

## Prerequisites
- Vercel account (https://vercel.com)
- GitHub repository connected to Vercel

## Step 1: Deploy to Vercel

### Option A: Using Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Click "Add New Project"
3. Select your GitHub repository
4. Vercel will auto-detect it's a React app
5. Click "Deploy"

### Option B: Using Vercel CLI
```bash
# Install Vercel CLI globally (if not already)
npm install -g vercel

# Deploy from your frontend directory
cd frontend
vercel
```

## Step 2: Configure Environment Variables

After deploying, set the following environment variables in your Vercel project settings:

### Settings → Environment Variables

1. **REACT_APP_USE_AGENT_ENGINE**
   - Value: `true` (for Agent Engine) or `false` (for local backend)
   - Required

2. **REACT_APP_API_BASE_URL** (if using local backend)
   - Value: Your backend API URL
   - Example: `https://api.example.com`
   - Only needed when `REACT_APP_USE_AGENT_ENGINE` is `false`

3. **REACT_APP_GOOGLE_CLIENT_ID** (if using Agent Engine)
   - Value: Your Google OAuth client ID
   - Only needed when `REACT_APP_USE_AGENT_ENGINE` is `true`

4. **REACT_APP_GCP_PROJECT_ID** (if using Agent Engine)
   - Value: `dev-dispatch-478502-p8`
   - Only needed when `REACT_APP_USE_AGENT_ENGINE` is `true`

5. **REACT_APP_AGENT_ENGINE_ID** (if using Agent Engine)
   - Value: `2664103479961714688`
   - Only needed when `REACT_APP_USE_AGENT_ENGINE` is `true`

## Step 3: Configure Deployment Settings (Optional)

In Vercel project settings:

1. **Build Settings**
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `build` (auto-detected)
   - Install Command: `npm ci` (recommended)

2. **Domains**
   - Configure custom domain if desired
   - Default Vercel domain is auto-assigned

## Features Included

### Security
- ✅ Cache control headers for static assets
- ✅ Immutable asset hashing
- ✅ SPA routing with client-side fallback

### Performance
- ✅ Automatic image optimization
- ✅ Code splitting with React
- ✅ Gzip compression enabled
- ✅ Edge caching for static assets (1 year)

### Build
- ✅ Clean build process
- ✅ No ESLint warnings
- ✅ Production-optimized bundle (~67KB gzipped)

## What's Been Configured

### vercel.json
- Specifies build command and output directory
- Maps environment variable references
- Configures HTTP headers for caching
- Sets up SPA routing with fallback to `/index.html`

### .vercelignore
- Excludes unnecessary files from deployment
- Removes test files and documentation
- Optimizes deployment package size

## Testing Locally Before Deployment

```bash
# Build the project
npm run build

# Test the build locally
npm install -g serve
serve -s build

# Your app will be at http://localhost:3000
```

## Post-Deployment

1. **Verify Deployment**
   - Visit your Vercel domain
   - Test all interactive features
   - Check browser console for errors

2. **Monitor Performance**
   - Use Vercel Analytics dashboard
   - Monitor Core Web Vitals
   - Check deployment logs

3. **Update Backend Integration**
   - If using local backend, ensure CORS is configured
   - Update backend URL if deploying backend to different host

## Troubleshooting

### Build Fails
- Check Vercel logs in project dashboard
- Ensure all environment variables are set correctly
- Verify Node.js version compatibility (18+)

### Blank Page or 404 Errors
- Verify SPA routing is working (vercel.json configured)
- Check browser console for errors
- Ensure static assets are loading (check cache headers)

### API Connection Issues
- Verify backend is accessible from Vercel region
- Check CORS headers on backend
- Confirm environment variables are correct

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Create React App Deployment](https://create-react-app.dev/docs/deployment/)
- [Vercel CLI Reference](https://vercel.com/docs/cli)
