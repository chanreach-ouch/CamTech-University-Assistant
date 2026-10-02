# Design Tokens

Since `wget` was unavailable in the build environment to download the full CSS page-requisites, we were unable to statically extract the Elementor CSS variables (`--e-global-color-*`) directly from the local files.

- **Primary Color:** unknown — inspect in browser DevTools
- **Accent Color:** unknown — inspect in browser DevTools
- **Typography/Font:** unknown — inspect in browser DevTools

The chat widget CSS is currently using CSS variables with fallback values, e.g.:
`background-color: var(--e-global-color-primary, #0056b3);`

This ensures that when the widget is injected into the real site (where the Elementor CSS variables are defined), it will automatically inherit the correct branding, and gracefully fallback to default blue if the variables are missing.
