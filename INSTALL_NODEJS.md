# Install Node.js

## Quick Install

1. Download Node.js LTS from: https://nodejs.org
2. Run the installer
3. Restart your terminal/command prompt
4. Verify installation:
   ```
   node --version
   npm --version
   ```

## After Installing Node.js

Run this to deploy:
```
deploy_all.bat
```

Or manually:
```
cd frontend
npm install
npm run build
cd ..
git add .
git commit -m "Deploy latest"
git push origin main
```
