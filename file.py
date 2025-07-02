import os

# Define your project structure
structure = {
    "public": [
        "favicon.ico",
        "placeholder.svg",
        "robots.txt"
    ],
    "src/components/ui": [
        "accordion.tsx", "alert-dialog.tsx", "alert.tsx", "aspect-ratio.tsx",
        "avatar.tsx", "badge.tsx", "breadcrumb.tsx", "button.tsx", "calendar.tsx",
        "card.tsx", "carousel.tsx", "chart.tsx", "checkbox.tsx", "collapsible.tsx",
        "command.tsx", "context-menu.tsx", "dialog.tsx", "drawer.tsx", "dropdown-menu.tsx",
        "form.tsx", "hover-card.tsx", "input-otp.tsx", "input.tsx", "label.tsx",
        "menubar.tsx", "navigation-menu.tsx", "pagination.tsx", "popover.tsx", "progress.tsx",
        "radio-group.tsx", "resizable.tsx", "scroll-area.tsx", "select.tsx", "separator.tsx",
        "sheet.tsx", "sidebar.tsx", "skeleton.tsx", "slider.tsx", "sonner.tsx",
        "switch.tsx", "table.tsx", "tabs.tsx", "textarea.tsx", "toast.tsx",
        "toaster.tsx", "toggle-group.tsx", "toggle.tsx", "tooltip.tsx"
    ],
    "src/components": [
        "AIChat.tsx", "AuthScreen.tsx", "Dashboard.tsx", "FileUpload.tsx",
        "Layout.tsx", "MetabaseEmbed.tsx", "ReportsView.tsx"
    ],
    "src/contexts": [
        "AuthContext.tsx"
    ],
    "src/hooks": [
        "use-mobile.tsx", "use-toast.ts"
    ],
    "src/lib": [
        "openrouter.ts", "supabase.ts", "utils.ts"
    ],
    "src/pages": [
        "HomePage.tsx", "NotFound.tsx"
    ],
    "src": [
        "App.css", "App.tsx", "index.css", "main.tsx", "vite-env.d.ts"
    ],
    ".": [  # root-level files
        "components.json", "eslint.config.js", "index.html", "package.json",
        "postcss.config.js", "README.md", "tailwind.config.ts",
        "tsconfig.app.json", "tsconfig.json", "tsconfig.node.json", "vite.config.ts"
    ]
}

# Create directories and files
for folder, files in structure.items():
    for file in files:
        file_path = os.path.join(folder, file)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            pass  # Creates an empty file

print("Project structure created successfully.")
