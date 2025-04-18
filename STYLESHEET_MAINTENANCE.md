# LocalLift Stylesheet Maintenance Guide

This document outlines the stylesheet build process and provides guidance on handling CSS modifications for the LocalLift application.

## Build Process Overview

LocalLift uses Tailwind CSS for styling. The build process involves:

1. Source Tailwind CSS file: `./frontend/styles/tailwind.css`
2. Output file: `./public/style.css`
3. Configuration: `tailwind.config.js`

## Build Commands

The following npm commands are available for CSS processing:

```bash
# Build CSS once
npm run build:css

# Watch for changes and rebuild
npm run watch:css

# Full build (includes CSS)
npm run build

# Vercel-specific build
npm run vercel-build
```

## Handling CSS Issues

If you encounter issues with Tailwind CSS not processing correctly:

1. **Manual CSS additions**: When Tailwind utility classes are not being processed correctly (common during deployment), you can add manual CSS to `public/style.css`. This is a fallback solution when the build process fails, so document any manual additions.

2. **Preserve existing CSS**: Before running a build, the current CSS is backed up to `public/style.backup.css` by the `preserve-css` script. You can use this to recover custom styles if they're overwritten.

3. **Common Tailwind Classes**: The most frequently used Tailwind classes have been added as regular CSS in the style.css file to ensure they work even if Tailwind processing fails.

## Deployment Considerations

### Vercel Deployment

The `vercel.json` file is configured to run the `vercel-build` script during deployment. This should automatically build the CSS.

Points to check if there are style issues after deployment:

1. Ensure the `buildCommand` in `vercel.json` is set to `npm run vercel-build`
2. Verify the GitHub Actions workflow is executing the CSS build steps
3. Check the deployment logs for CSS build errors

### Manual Style Overrides

If Tailwind continues to cause issues, you can:

1. Add essential styles directly to `public/style.css`
2. For responsive layouts, add media queries manually
3. Document any manual additions with comments for future reference

## Best Practices

1. **Use explicit CSS classes for critical elements**: Rather than relying solely on Tailwind utility classes for crucial UI elements, define explicit CSS classes that can be easily maintained.

2. **Test builds locally**: Before pushing changes, run `npm run build` locally to ensure CSS is compiled correctly.

3. **Commit built CSS**: For critical deployments, commit the built CSS files to ensure they're available even if the build process fails during deployment.

4. **Watch for version conflicts**: Tailwind updates may affect how utility classes are processed. Lock dependencies to specific versions to avoid unexpected changes.

## Troubleshooting Common Issues

### CSS Not Updating

If your CSS changes don't appear:
- Clear browser cache completely
- Verify the build command completed successfully
- Check for errors in the build logs

### Layout Breaking on Deployment

If layouts break on deployment but work locally:
- Verify the CSS was properly built during the deployment process
- Check for environment-specific styling issues
- Consider adding critical CSS directly to the style.css file

### Responsive Design Issues

If responsive design isn't working properly:
- Check media query syntax in both Tailwind config and manual CSS
- Ensure viewport meta tag is present in HTML
- Test across multiple devices and browsers

## Contact

For persistent stylesheet issues, contact the lead developer or raise an issue in the GitHub repository with screenshots and detailed descriptions of the problem.
