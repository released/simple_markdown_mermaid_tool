# Output Formats

## HTML

HTML is generated directly by the Python exporter. The output contains the current Markdown source and the JavaScript needed to render Markdown and Mermaid diagrams.

## PDF

PDF is rendered from the generated HTML through Microsoft Edge or Google Chrome in headless mode.
The exporter measures the fully rendered document first and uses that size for a single long PDF page when it is within Chromium's page-size limit.
If the rendered content exceeds that limit, the tool reports a warning and Chromium may paginate.

## PNG

PNG is rendered from the generated HTML through Microsoft Edge or Google Chrome in headless screenshot mode.
The exporter uses a full-page browser screenshot based on the rendered document size, so long Mermaid flowcharts are not limited to the visible viewport.

## JPG

JPG is rendered directly through Microsoft Edge or Google Chrome in headless screenshot mode.

## Browser Detection

The exporter checks in this order:

1. `MARKDOWN_MERMAID_BROWSER`
2. `msedge.exe`, `chrome.exe`, or `chromium.exe` in PATH
3. Common Windows Edge and Chrome install paths
