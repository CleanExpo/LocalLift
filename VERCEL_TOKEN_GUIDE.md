# How to Find Your Vercel Token and IDs

This guide explains how to locate the required Vercel credentials needed for setting up GitHub Actions CI/CD.

## Generating a Vercel Token

1. **Log in to your Vercel account** at [vercel.com](https://vercel.com/dashboard)

2. **Click on your profile picture** in the top-right corner, then select "Settings"

3. **Navigate to Tokens**
   - In the left sidebar, scroll down to find and click on "Tokens"

4. **Create a new token**
   - Click the "Create" button
   - Name: "LocalLift GitHub Actions"
   - Scope: Select "Full Access" (Required for CI/CD)
   - Click "Create Token"

5. **Copy the generated token immediately**
   - ⚠️ IMPORTANT: This token will only be shown once
   - Store it securely as you'll need it for GitHub Secrets

## Finding Your Vercel Organization ID

1. **Go to your Vercel Dashboard** at [vercel.com/dashboard](https://vercel.com/dashboard)

2. **Look at your browser URL**
   - If you're in a team/organization, the URL will look like:
     `https://vercel.com/team-name?orgId=org_XXXXXXXXXXXX`
   - If you're in a personal account, it may look like:
     `https://vercel.com/username?orgId=org_XXXXXXXXXXXX`

3. **Copy the `orgId` value**
   - This is the value after `orgId=` in the URL
   - For example, from the URL `https://vercel.com/admin-cleanexpo247s-projects?orgId=team_ABCDEF123`, 
     the Organization ID would be `team_ABCDEF123`

## Finding Your Vercel Project ID

1. **Go to your Vercel Dashboard** at [vercel.com/dashboard](https://vercel.com/dashboard)

2. **Click on the LocalLift project**
   - This will take you to the project overview page

3. **Go to Project Settings**
   - Click on the "Settings" tab at the top of the project page

4. **Find Project ID**
   - Scroll down in the General section
   - You'll see "Project ID" with a value like `prj_XXXXXXXXXXXX`
   - Copy this value

## Adding These Values to GitHub Secrets

Once you have all three Vercel values:

1. Go to your GitHub repository at [github.com/CleanExpo/LocalLift](https://github.com/CleanExpo/LocalLift)
2. Navigate to Settings → Secrets and variables → Actions
3. Add each of these as new repository secrets:
   - Name: `VERCEL_TOKEN` (Value: the token you generated)
   - Name: `VERCEL_ORG_ID` (Value: the org ID you found)
   - Name: `VERCEL_PROJECT_ID` (Value: the project ID you found)

These values, along with your Railway token (`RAILWAY_TOKEN: p 0e58b112-f5f5-4285-ad1f-f47d1481045b`), will enable GitHub Actions to automatically deploy your application whenever changes are pushed to the main branch.
