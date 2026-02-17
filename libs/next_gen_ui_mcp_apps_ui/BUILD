# Install npm dependencies
run_shell_command(
    name="npm_install",
    command="npm install",
    execution_dependencies=[":package_json"],
    workdir=".",
)

# Build the UI (produces dist/*.html files)
run_shell_command(
    name="build",
    command="npm run build",
    execution_dependencies=[
        ":npm_install",
        ":package_json",
        ":vite_config",
        ":tsconfig",
        ":sources",
        ":html_entries",
    ],
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

# Source files for TypeScript/React
files(
    name="sources",
    sources=["src/**/*.tsx", "src/**/*.ts"],
)
