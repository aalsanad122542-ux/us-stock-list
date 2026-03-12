# GitHub Actions Daily Email Setup Guide

This guide will set up your daily stock email to run on GitHub's free servers - no laptop needed!

## Prerequisites

1. A GitHub account (free)
2. Your project pushed to GitHub

---

## Step 1: Push Code to GitHub

Open terminal in your project folder:

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Add daily stock email with GitHub Actions"

# Create GitHub repo (do this on github.com first, then connect)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

---

## Step 2: Add Secrets

1. Go to your GitHub repo: https://github.com/YOUR_USERNAME/YOUR_REPO
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these:

| Secret Name | Value |
|-------------|-------|
|Get started with GitHub Actions
Build, test, and deploy your code. Make code reviews, branch management, and issue triaging work the way you want. Select a workflow to get started.

Skip this and set up a workflow yourself 

Search workflows
Suggested for this repository
Simple workflow
By GitHub

Simple workflow logo
Start with a file with the minimum necessary structure.

Deployment
View all
Deploy Node.js to Azure Web App
By Microsoft Azure

Deploy Node.js to Azure Web App logo
Build a Node.js project and deploy it to an Azure Web App.

Deployment
Deploy to Amazon ECS
By Amazon Web Services

Deploy to Amazon ECS logo
Deploy a container to an Amazon ECS service powered by AWS Fargate or Amazon EC2.

Deployment
Build and Deploy to GKE
By Google Cloud

Build and Deploy to GKE logo
Build a docker container, publish it to Google Container Registry, and deploy to GKE.

Deployment
Terraform
By HashiCorp

Terraform logo
Set up Terraform CLI in your GitHub Actions workflow.

Deployment
Deploy to Alibaba Cloud ACK
By Alibaba Cloud

Deploy to Alibaba Cloud ACK logo
Deploy a container to Alibaba Cloud Container Service for Kubernetes (ACK).

Deployment
Deploy to IBM Cloud Kubernetes Service
By IBM

Deploy to IBM Cloud Kubernetes Service logo
Build a docker container, publish it to IBM Cloud Container Registry, and deploy to IBM Cloud Kubernetes Service.

Deployment
Tencent Kubernetes Engine
By Tencent Cloud

Tencent Kubernetes Engine logo
This workflow will build a docker container, publish and deploy it to Tencent Kubernetes Engine (TKE).

Deployment
OpenShift
By Red Hat

OpenShift logo
Build a Docker-based project and deploy it to OpenShift.

Deployment
Continuous integration
View all
Elixir
By GitHub Actions

Elixir logo
Build and test an Elixir project with Mix.

Elixir
Android CI
By GitHub Actions

Android CI logo
Build an Android project with Gradle.

Java
Java with Gradle
By GitHub Actions

Java with Gradle logo
Build and test a Java project using a Gradle wrapper script.

Java
Laravel
By GitHub Actions

Laravel logo
Test a Laravel project.

PHP
Automation
View all
Manual workflow
By GitHub Actions

Simple workflow that is manually triggered.

Automation
Greetings
By GitHub Actions

Greets users who are first time contributors to the repo

Automation
AI issue summary
By GitHub Actions

Summarizes new issues

Automation
Labeler
By GitHub Actions

Labels pull requests based on the files changed

Automation
Pages
View all
Jekyll
By GitHub Actions

Jekyll logo
Package a Jekyll site.

GitHub Pages Jekyll
By GitHub Actions

GitHub Pages Jekyll logo
Package a Jekyll site with GitHub Pages dependencies preinstalled.

Gatsby
By GitHub Actions

Gatsby logo
Package a Gatsby site.

Next.js
By GitHub Actions

Next.js logo
Package a Next.js site.

Browse all categories
Deployment
Continuous integration
Automation
Pages

---

## Step 3: Verify Setup

1. Go to **Actions** tab in your GitHub repo
2. You should see the "Daily Stock Email" workflow
3. Click on it → Click **Run workflow** → Click **Run workflow** (green button)
4. Wait 1-2 minutes, refresh page
5. Click the run → Check **build** step logs
6. Look for "Daily stock email sent successfully"

---

## Step 4: Confirm Schedule

The workflow runs automatically at:
- 04:00 UTC
- 08:00 UTC  
- 12:00 UTC
- 16:00 UTC
- 20:00 UTC

Each email analyzes 5 stocks = 25 stocks/day total.

---

## Troubleshooting

**If workflow fails:**

1. Check the error in Actions → Click failed run → See logs
2. Common issues:
   - Invalid secrets → Re-add them
   - API rate limit → Wait and retry
   - Missing dependency → Check requirements.txt

**To run manually:**
- Go to Actions → Daily Stock Email → Run workflow

---

## Cost

- **GitHub Actions Free Tier:** 2000 minutes/month
- **Your usage:** ~50 min/day × 30 days = 1500 min/month
- **Result:** FREE ✓

---

## Optional: Get ApiFreeLLM API Key (Backup AI)

1. Go to https://apifreellm.com
2. Sign in with Google
3. Get your free API key
4. Add secret: `APIFREELLM_API_KEY` = your key

This is optional - Gemini will be used first, ApiFreeLLM as backup.
