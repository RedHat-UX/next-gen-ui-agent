# Install npm dependencies
run_shell_command(
    name="npm_install",
    command="npm install",
    execution_dependencies=[":package_json"],
    workdir=".",
)

# Build the UI (produces dist/*.html files).
# shell_command (not run_shell_command) so this runs during `pants package` when
# depended on by the MCP docker image / distribution. Runs npm install in-sandbox
# so node_modules exists before build.
shell_command(
    name="build",
    command="npm install && npm run build",
    tools=["node", "npm", "npx", "bash", "sh"],
    execution_dependencies=[
        ":package_json",
        ":vite_config",
        ":tsconfig",
        ":sources",
        ":html_entries",
    ],
    output_directories=["dist"],
    timeout=300,  # CI can be slow; npm install + build often exceeds default 30s
    workdir=".",
)

# Make package.json and config files available
files(
    name="package_json",
    sources=["package.json", "package-lock.json"],
)

files(
    name="vite_config",
    sources=["vite.config.ts"],
)

files(
    name="tsconfig",
    sources=["tsconfig.json"],
)

files(
    name="html_entries",
    sources=["*.html"],
)

# Source files for TypeScript/CSS (vanilla JS app)
files(
    name="sources",
    sources=["src/**/*.ts", "src/**/*.css"],
)
