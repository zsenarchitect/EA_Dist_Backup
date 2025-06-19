# GitHub Pages Setup Guide for Distribution Repositories

## Automatic Setup
This script automatically configures GitHub Pages for your repository. Here's what it creates:

### Files Created:
- `docs/` - Documentation directory in repository root (GitHub Pages source)
- `.nojekyll` - Disables Jekyll processing for faster builds
- `404.html` - Custom 404 error page
- `robots.txt` - SEO configuration for search engines
- `sitemap.xml` - Site map for better SEO
- `.github/workflows/deploy-docs.yml` - GitHub Actions workflow for auto-deployment

### Important Directory Structure:
- `docs/` - This is the ONLY docs folder that should exist (in repository root)
- `Website/docs/` - This folder will be created temporarily but should be ignored
- GitHub Pages will serve content from the root `docs/` folder

### Repository Configuration Required:
1. Go to your repository Settings
2. Navigate to Pages section
3. Set Source to "GitHub Actions"
4. The workflow will automatically deploy on push to main/master

### Custom Domain Setup (Optional):
1. Update the `custom_domain` in the GITHUB_PAGES_CONFIG
2. Add a CNAME record in your DNS pointing to: [username].github.io
3. The script will automatically create the CNAME file

### For Distribution Repositories:
1. Copy this entire Website folder to your distribution repository
2. Update the GITHUB_PAGES_CONFIG with your repository details
3. Run `python static_webpage_publish.py`
4. Enable GitHub Pages in repository settings

### Troubleshooting:
- If site appears empty, check GitHub Pages source is set to "GitHub Actions"
- Ensure the workflow has permissions to deploy (check repository Settings > Actions)
- Verify all required files are in the root `docs/` folder (not Website/docs/)
- Delete any duplicate `Website/docs/` folder if it exists

### URLs:
- Repository: https://github.com/{GITHUB_PAGES_CONFIG['organization']}/{GITHUB_PAGES_CONFIG['repo_name']}
- Live Site: {GITHUB_PAGES_CONFIG['site_url']}
