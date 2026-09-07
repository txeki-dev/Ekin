"""Interface strings, centralized to make a future translation easy.

Usage: `from strings import t` and `t("dotted.key")`, or `t("key", name=value)` for the
ones that interpolate (uses `str.format`). English is the active language -- STRINGS is a
flat dict with no language-selection mechanism yet -- but moving every visible string here
keeps the ground ready to add a second language later without touching the rest of the code.

Emoji were removed from these values on purpose: icons are now drawn with Lucide (see
`icons.py`), so labels here carry text only.
"""

STRINGS = {
    # --- main.py: ventana principal, bandeja, actualizaciones, datos de ejemplo ---
    "main.window_title": "Ekin v{version}",
    "main.tray.tooltip": "Ekin Kanban",
    "main.tray.open": "Open Ekin",
    "main.tray.quit": "Quit",
    "main.tray.due_today_title": "Ekin — {count} task(s) due today",
    "main.update.available_title": "Update available",
    "main.update.available_body": (
        "A new version of Ekin Kanban is available on GitHub.\n"
        "Do you want to download it and restart the app now?"
    ),
    "main.update.done_title": "Updated",
    "main.update.done_body": "The app updated successfully. It will restart now.",
    "main.onboarding.board_name": "My First Board",
    "main.onboarding.col_todo": "To do",
    "main.onboarding.col_doing": "In progress",
    "main.onboarding.col_done": "Done",
    "main.onboarding.task_title": "Explore Ekin Kanban",
    "main.onboarding.task_description": (
        "Welcome!\n\nThis is a task card. Click it to:\n"
        "- Change the title\n"
        "- Add a description\n"
        "- Set custom tags\n"
        "- Log your progress in the personal Journal (on the right)"
    ),
    "main.onboarding.tag_category": "Priority",
    "main.onboarding.tag_value": "High",
    "main.onboarding.log_entry": "Initialized the app for the first time. All set to start working!",

    # --- board_view.py: tablero, columnas, tareas ---
    "board_view.column_edit.new_title": "New column",
    "board_view.column_edit.edit_title": "Edit column",
    "board_view.column_edit.name_label": "<b>Column name:</b>",
    "board_view.column_edit.name_placeholder": "e.g. Inbox, In progress...",
    "board_view.column_edit.color_label": "<b>Accent color:</b>",
    "board_view.column_edit.color_dialog_title": "Select column color",
    "board_view.column_edit.save": "Save",
    "board_view.column_edit.cancel": "Cancel",
    "board_view.column_edit.warn_title": "Heads up",
    "board_view.column_edit.warn_empty_name": "The column name can't be empty.",
    "board_view.board_selection.target_label": "<b>Select the destination board:</b>",
    "board_view.board_selection.cancel": "Cancel",
    "board_view.board_selection.no_other_boards": "No other boards",
    "board_view.header.toggle_sidebar_tooltip": "Show/hide sidebar",
    "board_view.header.default_title": "My Board",
    "board_view.header.counts": "{tasks} tasks · {due} due this week",
    "board_view.welcome": (
        "Welcome to Ekin Kanban!\n\n"
        "Create your first board in the sidebar\n"
        "to start organizing your tasks and journals."
    ),
    "board_view.add_column_btn": "New column",
    "board_view.delete_column.title": "Delete column",
    "board_view.delete_column.body": (
        "Delete the column '{name}'?\n"
        "Its tasks, their journals and links go with it. Ctrl + Z restores the whole column."
    ),
    "board_view.delete_column.undo_label": "Delete column",
    "board_view.copy_column.title": "Copy column",
    "board_view.copy_column.action": "Copy",
    "board_view.copy_column.fallback_board_name": "the selected board",
    "board_view.copy_column.done_title": "Column copied",
    "board_view.copy_column.done_body": (
        "The column '{column}' and all its tasks/logs were copied to '{board}'."
    ),
    "board_view.add_task.title": "New task",
    "board_view.add_task.prompt": "Enter the task title:",
    "board_view.delete_task.undo_label": "Delete task",

    # --- widgets.py: tarjetas, columnas (tooltips/menú), etiquetas ---
    "widgets.card.board_link_tooltip": "Go to linked board",
    "widgets.column.collapse_tooltip": "Collapse column",
    "widgets.column.expand_tooltip": "Expand column",
    "widgets.column.edit_tooltip": "Edit column (options: edit, copy, delete)",
    "widgets.column.title_drag_tooltip": "Drag to reorder or move this column to another board",
    "widgets.column.task_count_tooltip": "{count} task(s)",
    "widgets.column.add_task_btn": "Add task",
    "widgets.column.menu_edit": "Edit column",
    "widgets.column.menu_copy": "Copy to another board...",
    "widgets.column.menu_delete": "Delete column",

    # --- sidebar.py: campana, tableros, barra de utilidades, exportar ---
    "sidebar.title": "EKIN",
    "sidebar.boards_subtitle": "Boards",
    "sidebar.add_board_btn": "New board",
    "sidebar.edit_board_btn": "Edit",
    "sidebar.copy_board_btn": "Copy",
    "sidebar.delete_board_btn": "Delete",
    "sidebar.archived_btn": "Archived boards",
    "sidebar.archived_tooltip": "Show/hide archived boards (right-click a board to archive)",
    "sidebar.export_btn": "Export",
    "sidebar.export_tooltip": "Export boards to JSON, CSV or Markdown",
    "sidebar.import_btn": "Import",
    "sidebar.import_tooltip": "Import boards, columns and tasks from a JSON file",
    "sidebar.board_config_tooltip": "Board options",
    "sidebar.board_config.title": "Board options",
    "sidebar.bell_tooltip": "Overdue tasks or due today/tomorrow",
    "sidebar.search_tooltip": "Search tasks (Ctrl+F)",
    "sidebar.calendar_tooltip": "Open calendar view",
    "sidebar.settings_tooltip": "Settings (theme, notifications)",
    "sidebar.shortcuts_tooltip": "Keyboard shortcuts (Ctrl+/)",
    "sidebar.notifications.header": "Due soon",
    "sidebar.notifications.empty": "No overdue or upcoming tasks.",
    "sidebar.notifications.group_overdue": "OVERDUE",
    "sidebar.notifications.group_today": "TODAY",
    "sidebar.notifications.group_tomorrow": "TOMORROW",
    "sidebar.notifications.item_no_title": "(untitled)",
    "sidebar.notifications.item_tooltip": "{board} · due {due_date}",
    "sidebar.board_button.archived_tooltip": "Archived board — right-click to unarchive",
    "sidebar.board_button.menu_unarchive": "Unarchive board",
    "sidebar.board_button.menu_archive": "Archive board",
    "sidebar.board_edit.new_title": "New board",
    "sidebar.board_edit.edit_title": "Edit board",
    "sidebar.board_edit.copy_title": "Copy board",
    "sidebar.board_edit.copy_default_name": "{name} - Copy",
    "sidebar.board_edit.name_label": "<b>Board name:</b>",
    "sidebar.board_edit.name_placeholder": "e.g. Work, Personal, Trip...",
    "sidebar.board_edit.color_label": "<b>Board color:</b>",
    "sidebar.board_edit.color_dialog_title": "Select board color",
    "sidebar.board_edit.save": "Save",
    "sidebar.board_edit.cancel": "Cancel",
    "sidebar.board_edit.warn_title": "Heads up",
    "sidebar.board_edit.warn_empty_name": "The board name can't be empty.",
    "sidebar.export_menu.json": "JSON (.json)",
    "sidebar.export_menu.csv": "Tasks CSV (.csv)",
    "sidebar.export_menu.markdown": "Markdown report (.md)",
    "sidebar.export.dialog_title": "Export {label}",
    "sidebar.export.error_title": "Export error",
    "sidebar.export.error_body": "Could not export:\n{error}",
    "sidebar.export.done_title": "Exported",
    "sidebar.export.done_body": "{label} export saved to:\n{path}",
    "sidebar.delete_board.title": "Delete board",
    "sidebar.delete_board.body": (
        "Delete the board '{name}'?\n"
        "All its columns, tasks and journals go with it permanently."
    ),
    "sidebar.delete_board.undo_label": "Delete board",

    # --- export_dialog.py & import_dialog.py: exportación e importación avanzada ---
    "export_dialog.window_title": "Export boards",
    "export_dialog.scope_group": "<b>Export scope:</b>",
    "export_dialog.scope_all": "All boards (including archived)",
    "export_dialog.scope_current": "Only the active board: «{name}»",
    "export_dialog.format_group": "<b>File format:</b>",
    "export_dialog.format_json": "JSON (.json) — Full data or templates",
    "export_dialog.json_include_tasks": "Include tasks, tags, links and journal",
    "export_dialog.json_template_hint": "If unchecked, only the column structure is exported as a reusable template.",
    "export_dialog.format_csv": "CSV (.csv) — Task list for spreadsheets (Excel / Sheets)",
    "export_dialog.format_markdown": "Markdown (.md) — Readable project report",
    "export_dialog.md_include_details": "Include descriptions, links and journal in the report",
    "export_dialog.export_btn": "Export to file...",
    "export_dialog.cancel_btn": "Cancel",
    "export_dialog.save_title": "Save export file",
    "export_dialog.done_title": "Export complete",
    "export_dialog.done_body": "{label} export saved successfully to:\n{path}",
    "export_dialog.error_title": "Export error",
    "export_dialog.error_body": "Could not complete the export:\n{error}",

    "import_dialog.window_title": "Import boards from JSON",
    "import_dialog.open_title": "Select a JSON file to import",
    "import_dialog.file_label": "<b>File:</b> {filename}",
    "import_dialog.summary_label": "Detected <b>{boards}</b> board(s), <b>{columns}</b> column(s) and <b>{tasks}</b> task(s).",
    "import_dialog.options_group": "<b>Import options:</b>",
    "import_dialog.opt_full": "Import everything (boards, columns, tasks, tags, links and journal)",
    "import_dialog.opt_structure_only": "Import only the column structure (as a template without tasks)",
    "import_dialog.template_only_hint": "This file contains only column structure (a template).",
    "import_dialog.import_btn": "Import to Ekin",
    "import_dialog.cancel_btn": "Cancel",
    "import_dialog.done_title": "Import complete",
    "import_dialog.done_body": "Imported {count} board(s) successfully.",
    "import_dialog.error_title": "Import error",
    "import_dialog.error_body": "Could not import the file:\n{error}",

    # --- calendar_view.py: vista de calendario + ajustes de sincronización .ics ---
    "calendar.chip_no_title": "(untitled)",
    "calendar.chip_tooltip": "{board} · {title}\nDrag to another day to reschedule",
    "calendar.more_tasks": "+{count} more",
    "calendar.today_btn": "Today",
    "calendar.mode_month": "Month",
    "calendar.mode_week": "Week",
    "calendar.mode_day": "Day",
    "calendar.mode_tooltip": "Calendar view",
    "calendar.board_filter_tooltip": "Filter by board",
    "calendar.settings_btn": "Settings",
    "calendar.settings_tooltip": "Sync / export to Google, Apple or Outlook",
    "calendar.close_btn": "Back to board",
    "calendar.close_tooltip": "Back to the board view",
    "calendar.all_boards": "All boards",
    "calendar.week_period": "Week {start} – {end}",
    "calendar.error_title": "Error",

    "calendar.settings_dialog.title": "Calendar settings",
    "calendar.settings_dialog.header": "<b>Calendar sync</b>",
    "calendar.settings_dialog.info": (
        "Ekin exports your tasks with a due date to a standard "
        "<b>iCalendar (.ics)</b> file, compatible with Google Calendar, Apple Calendar and Outlook."
    ),
    "calendar.settings_dialog.sync_title": "<b>Automatic sync</b> (recommended)",
    "calendar.settings_dialog.sync_desc": (
        "Ekin keeps a .ics file <b>always up to date</b> (rewriting it whenever tasks "
        "change). Save it in a Dropbox / OneDrive / Google Drive folder and "
        "<b>subscribe</b> to it once: from then on it updates itself."
    ),
    "calendar.settings_dialog.sync_board_tooltip": "Automatically sync all boards or just one",
    "calendar.settings_dialog.configure_btn_initial": "Choose file…",
    "calendar.settings_dialog.configure_btn_change": "Change file…",
    "calendar.settings_dialog.disable_btn": "Disable",
    "calendar.settings_dialog.subscribe_title": "<b>Subscribe in your calendar</b>",
    "calendar.settings_dialog.subscribe_desc": (
        "Upload the .ics file to a public folder (Google Drive / Dropbox / OneDrive) "
        "and paste its <b>public URL</b> here. Ekin saves it and, depending on the button, "
        "copies it to the clipboard and opens the provider's page to <b>add a calendar by URL</b> "
        "(the manual step that often fails). Detailed guide below."
    ),
    "calendar.settings_dialog.public_url_placeholder": "https://…/ekin_calendario.ics",
    "calendar.settings_dialog.google_btn_tooltip": "Copy the URL and open Google Calendar's «Add by URL»",
    "calendar.settings_dialog.outlook_btn_tooltip": "Copy the URL and open Outlook's «Subscribe from web»",
    "calendar.settings_dialog.apple_btn_tooltip": "Copy the URL as a webcal:// link for iPhone/Mac",
    "calendar.export_once_btn": "Export a copy…",
    "calendar.export_once_tooltip": "Save a one-off .ics snapshot to another location",
    "calendar.export_board_tooltip": "Export the calendar of all boards or just one",
    "calendar.settings_dialog.close_btn": "Close",
    "calendar.settings_dialog.sync_active": "Syncing to:<br><code>{path}</code>",
    "calendar.settings_dialog.sync_inactive": "Automatic sync disabled.",
    "calendar.settings_dialog.configure_file_dialog_title": "Sync file",
    "calendar.settings_dialog.configure_error_body": "Could not create the file:\n{error}",
    "calendar.settings_dialog.sync_activated_title": "Sync enabled",
    "calendar.settings_dialog.sync_activated_body": (
        "Ekin will keep {count} task(s) synced at:\n{path}\n\n"
        "Subscribe to this file once from your calendar and it will update itself."
    ),
    "calendar.settings_dialog.empty_url_title": "Empty URL",
    "calendar.settings_dialog.empty_url_body": (
        "Paste the public URL of your .ics file first (the shared link of the cloud folder "
        "where you sync it)."
    ),
    "calendar.settings_dialog.google_title": "Google Calendar",
    "calendar.settings_dialog.google_body": (
        "I copied the URL to the clipboard and opened Google Calendar (on the computer; "
        "the mobile app can't add by URL).\n\n"
        "1. Left side menu → «Other calendars» → «+» → «From URL».\n"
        "2. Paste the URL (Ctrl+V) and click «Add calendar».\n\n"
        "Note: Google reloads URL calendars slowly (every few hours, up to ~24 h) and it "
        "can't be forced."
    ),
    "calendar.settings_dialog.outlook_title": "Outlook Calendar",
    "calendar.settings_dialog.outlook_body": (
        "I copied the URL to the clipboard and opened Outlook in the browser.\n\n"
        "1. In Outlook.com: «Add calendar» → «Subscribe from web».\n"
        "   (In work/Microsoft 365 Outlook the path is outlook.office.com → same option.)\n"
        "2. Paste the URL (Ctrl+V), give it a name and color, and click «Import»/«Subscribe».\n\n"
        "Desktop Outlook (classic) also supports: Home → «Open calendar» → "
        "«From Internet…» and paste the URL."
    ),
    "calendar.settings_dialog.apple_title": "Apple / iCloud",
    "calendar.settings_dialog.apple_body": (
        "I copied the URL as a <b>webcal://</b> link to the clipboard (so iOS/macOS "
        "recognize it as a subscription). Paste it here:\n\n"
        "• iPhone/iPad: Settings → Calendar → Accounts → Add account → Other → "
        "«Add subscribed calendar» → paste the link → Next.\n"
        "• Mac (Calendar app): File → «New calendar subscription…» → paste the link → "
        "Subscribe; there you can set the refresh frequency (even every few minutes).\n\n"
        "The subscription is saved in iCloud and shows on all your Apple devices."
    ),
    "calendar.settings_dialog.provider_guide": (
        "<b>How to subscribe (stays in sync, no duplicates)</b>"
        "<p><b>0) Get a public, direct URL to the .ics.</b> Save the file in a cloud "
        "folder and share the link <i>directly to the file</i> (not to a preview page):"
        "<ul>"
        "<li><b>Google Drive</b>: share as «Anyone with the link». The normal link points to "
        "an HTML view; use the direct-download form "
        "<code>https://drive.google.com/uc?export=download&id=FILE_ID</code>.</li>"
        "<li><b>Dropbox</b>: copy the link and change the trailing <code>?dl=0</code> to "
        "<code>?dl=1</code>.</li>"
        "<li><b>OneDrive</b>: «Share» → «Anyone with the link» → copy the link.</li>"
        "</ul>"
        "Open it in an incognito window: you should see text starting with "
        "<code>BEGIN:VCALENDAR</code>. If you see a login or a preview, the link won't work.</p>"
        "<p><b>Google Calendar</b> (computer only): side menu → «Other calendars» → "
        "«+» → «From URL» → paste the URL → «Add calendar». Slow refresh (several hours).</p>"
        "<p><b>Outlook</b>: in <i>Outlook.com/365 (web)</i> → «Add calendar» → «Subscribe "
        "from web» → paste the URL → name/color → «Import». In <i>desktop Outlook</i> → "
        "Home → «Open calendar» → «From Internet…» → paste the URL.</p>"
        "<p><b>Apple / iCloud</b> (use a <code>webcal://</code> link): "
        "<i>iPhone/iPad</i> → Settings → Calendar → Accounts → Add account → Other → «Add "
        "subscribed calendar» → paste the link. <i>Mac</i> → Calendar app → File → «New "
        "calendar subscription…» → paste the link (you can choose how often it updates).</p>"
        "<p><b>Subscribe ≠ Import.</b> «Import» a copy is a fixed snapshot: it doesn't reflect "
        "changes or deletions and may duplicate events. Subscribe to the URL so it updates itself.</p>"
    ),
    "calendar.export_dialog_title": "Export a calendar copy",
    "calendar.export_error_body": "Could not export the calendar:\n{error}",
    "calendar.export_done_title": "Exported",
    "calendar.export_done_body": (
        "Exported {count} dated task(s) to:\n{path}\n\n"
        "Remember: an imported copy is a fixed snapshot; to keep it up to date, "
        "use the automatic sync above and subscribe to the file."
    ),

    # --- search_dialog.py: búsqueda global de tareas ---
    "search.window_title": "Search tasks",
    "search.header": "<b>Search tasks</b>",
    "search.text_placeholder": "Title or description…",
    "search.all_boards": "All boards",
    "search.all_tags": "All tags",
    "search.only_due_checkbox": "Only with a due date",
    "search.close_btn": "Close",
    "search.result_count": "{count} result(s)",
    "search.no_results": "No results.",
    "search.result_no_title": "(untitled)",
    "search.result_tooltip": "{board} · {column}",

    # --- settings_dialog.py: pantalla de Ajustes (tema, notificaciones) ---
    "settings.window_title": "Settings",
    "settings.header": "Settings",
    "settings.theme_label": "Theme",
    "settings.theme_dark": "Dark",
    "settings.theme_light": "Light",
    "settings.theme_desc": "Applies immediately — no restart.",
    "settings.notifications_label": "Windows notifications for tasks due today",
    "settings.notifications_checkbox": "Show Windows alerts for tasks due today",
    "settings.notifications_desc": "One summary when Ekin starts, then once a day.",
    "settings.timer_alert_label": "Warn on the card when a timer runs longer than",
    "settings.timer_alert_suffix": " h",
    "settings.timer_alert_desc": "Stale tasks turn terracotta on the board.",
    "settings.geometry_hint": "The window size and position are remembered automatically.",
    "settings.close_btn": "Close",

    # --- shortcuts_dialog.py: diálogo "Atajos de teclado" (Ctrl+/) ---
    "shortcuts.window_title": "Keyboard shortcuts",
    "shortcuts.header": "<b>Keyboard shortcuts</b>",
    "shortcuts.section_general": "General & navigation",
    "shortcuts.section_editor": "Rich text — notes & journal",
    "shortcuts.item_search": "Ctrl+F — Global search",
    "shortcuts.item_new_task": (
        "Ctrl+N — New task in the last column you interacted with (if none, the first "
        "column of the active board); inside the text editor, Ctrl+N is Bold"
    ),
    "shortcuts.item_new_column": "Ctrl+Shift+N — New column in the active board",
    "shortcuts.item_prev_next_board": "Alt+↑ / Alt+↓ — Previous / next board",
    "shortcuts.item_jump_board": "Ctrl+1 … Ctrl+9 — Jump straight to board № in the sidebar",
    "shortcuts.item_calendar": "Ctrl+Shift+C — Open the calendar",
    "shortcuts.item_settings": "Ctrl+, — Open Settings",
    "shortcuts.item_shortcuts": "Ctrl+/ — Show this window",
    "shortcuts.item_undo_redo": "Ctrl+Z / Ctrl+Y (or Ctrl+Shift+Z) — Undo / redo",
    "shortcuts.item_close_dialog": "Esc — Close the open dialog",
    "shortcuts.item_bold": "Ctrl+B or Ctrl+N — Bold (inside the editor)",
    "shortcuts.item_italic": "Ctrl+K or Ctrl+I — Italic (inside the editor)",
    "shortcuts.item_strike": "Ctrl+Shift+X — Strikethrough (inside the editor)",
    "shortcuts.item_align": "Ctrl+L / Ctrl+E / Ctrl+R / Ctrl+J — Align text (left, center, right, justify)",
    "shortcuts.item_case": "Ctrl+Shift+U / Ctrl+Shift+L / Shift+F3 — UPPERCASE / lowercase",
    "shortcuts.item_nest_bullet": "Tab (on a bullet) — Nest the bullet (inside the editor)",
    "shortcuts.item_arrow": "Typing «-->» becomes → automatically (inside the editor)",
    "shortcuts.item_add_log": "Ctrl+Enter — Add the note to the journal (task detail)",
    "shortcuts.hint": "Press Ctrl+/ anytime to see this window again.",
    "shortcuts.close_btn": "Close",

    # --- detail_dialog/markdown_edit.py: editor de texto enriquecido (barra de formato) ---
    "markdown_edit.bold_tooltip": "Bold (Ctrl+B or Ctrl+N)",
    "markdown_edit.italic_tooltip": "Italic (Ctrl+K or Ctrl+I)",
    "markdown_edit.strike_tooltip": "Strikethrough (Ctrl+Shift+X)",
    "markdown_edit.align_left_tooltip": "Align left (Ctrl+L)",
    "markdown_edit.align_center_tooltip": "Center text (Ctrl+E)",
    "markdown_edit.align_right_tooltip": "Align right (Ctrl+R)",
    "markdown_edit.align_justify_tooltip": "Justify text (Ctrl+J)",
    "markdown_edit.upper_tooltip": "Convert to UPPERCASE (Ctrl+Shift+U)",
    "markdown_edit.lower_tooltip": "Convert to lowercase (Ctrl+Shift+L)",
    "markdown_edit.context_upper": "Convert to UPPERCASE",
    "markdown_edit.context_lower": "Convert to lowercase",
    "markdown_edit.bullet_tooltip": "Bulleted list  ·  also with «* », «- » or «+ »",
    "markdown_edit.hr_tooltip": "Horizontal rule  ·  also by typing «---»",
    "markdown_edit.arrow_tooltip": "Insert arrow (→)  ·  also by typing «-->»",
    "markdown_edit.color_tooltip": "Text color",
    "markdown_edit.color_default": "Default color",
    "markdown_edit.color_more": "More colors…",
    "markdown_edit.color_dialog_title": "Select text color",
    "markdown_edit.table_tooltip": "Insert table",
    "markdown_edit.table_dialog_title": "Insert table",
    "markdown_edit.table_rows_label": "Rows:",
    "markdown_edit.table_cols_label": "Columns:",
    "markdown_edit.code_tooltip": "Insert code block  ·  also with «```»",
    "markdown_edit.code_dialog_title": "Insert code block",
    "markdown_edit.code_lang_label": "Programming language:",
    "markdown_edit.code_text_label": "Code:",
    "markdown_edit.code_insert_btn": "Insert",
    "markdown_edit.code_cancel_btn": "Cancel",
    "markdown_edit.delete_code_btn": "Delete",
    "markdown_edit.delete_code_tooltip": "Delete this code block",
    "markdown_edit.delete_code_btn_menu": "Delete code block",
    "markdown_edit.link_tooltip": "Insert web link (URL)",
    "markdown_edit.link_dialog_title": "Insert link",
    "markdown_edit.link_url_label": "Web address (URL):",
    "markdown_edit.link_text_label": "Display text (optional):",
    "markdown_edit.link_insert_btn": "Insert",
    "markdown_edit.link_cancel_btn": "Cancel",

    # --- detail_dialog/log_entry.py: entrada del diario/chat ---
    "log_entry.edit_tooltip": "Edit comment",
    "log_entry.delete_tooltip": "Delete comment",
    "log_entry.save_btn": "Save",
    "log_entry.cancel_btn": "Cancel",

    # --- detail_dialog/image_preview_dialog.py: vista ampliada de una imagen pegada ---
    "image_preview.window_title": "Image preview",

    # --- detail_dialog/tag_manager_dialog.py: gestor del catálogo de etiquetas ---
    "tag_manager.window_title": "Manage tags",
    "tag_manager.header": "<b>Tags</b>",
    "tag_manager.add_category_btn": "New",
    "tag_manager.category_action_label": "Rename tag",  # tooltip + QInputDialog title (misma frase)
    "tag_manager.delete_category_tooltip": "Delete tag",  # tooltip + QMessageBox title (misma frase)
    "tag_manager.values_title_default": "<b>Values</b>",
    "tag_manager.values_title_for_category": "<b>Values of «{category}»</b>",
    "tag_manager.new_value_placeholder": "New value (e.g. High)…",
    "tag_manager.new_value_color_tooltip": "Color of the new value",
    "tag_manager.add_value_btn": "Add value",
    "tag_manager.close_btn": "Close",
    "tag_manager.add_category_dialog_title": "New tag",
    "tag_manager.add_category_prompt": "Tag name (e.g. Priority):",
    "tag_manager.new_name_prompt": "New name:",  # usado al renombrar etiqueta y al renombrar valor
    "tag_manager.delete_category_body": (
        "Delete the tag «{category}» and all its values?\n"
        "It will be removed from every task that uses it."
    ),
    "tag_manager.no_category_hint": "Create or select a tag on the left to define its values.",
    "tag_manager.no_values_hint": "No values yet. Add the first one below.",
    "tag_manager.swatch_tooltip": "Change color",
    "tag_manager.rename_value_tooltip": "Rename value",  # tooltip + QInputDialog title (misma frase)
    "tag_manager.delete_value_tooltip": "Delete value",  # tooltip + QMessageBox title (misma frase)
    "tag_manager.color_dialog_title": "Value color",
    "tag_manager.warn_title": "Heads up",
    "tag_manager.duplicate_value_body": "A value with that name already exists in this tag.",
    "tag_manager.delete_value_body": (
        "Delete the value «{value}»?\nIt will be removed from the tasks it's assigned to."
    ),

    # --- detail_dialog/tag_picker_dialog.py: asignar/editar una etiqueta en una tarea ---
    "tag_picker.title_edit": "Edit tag",
    "tag_picker.title_assign": "Assign tag",
    "tag_picker.category_label": "<b>Tag</b>",
    "tag_picker.value_label": "<b>Value</b>",
    "tag_picker.manage_btn": "Manage tags…",
    "tag_picker.accept_btn": "OK",
    "tag_picker.cancel_btn": "Cancel",
    "tag_picker.none_option": "— None (hide) —",
    "tag_picker.no_categories_hint": "No tags defined. Use «Manage tags…» to create one.",
    "tag_picker.no_values_hint": "This tag has no values. Add them in «Manage tags…».",
    "tag_picker.warn_title": "Heads up",
    "tag_picker.warn_no_category": "Create a tag first in «Manage tags…».",
    "tag_picker.warn_no_value": "Select a value (or create it in «Manage tags…»).",

    # --- detail_dialog/task_detail_dialog.py: diálogo principal de detalle de tarea ---
    "task_detail.window_title": "Task details",
    "task_detail.title_label": "<b>Task title</b>",
    "task_detail.title_placeholder": "e.g. Write the monthly report...",
    "task_detail.description_label": "<b>Description / Notes</b>",
    "task_detail.description_placeholder": "Add details about this task...",
    "task_detail.timer_label": "<b>Timer:</b>",
    "task_detail.timer_start_btn": "Start",
    "task_detail.timer_restart_btn": "Restart",
    "task_detail.timer_clear_btn": "Stop",
    "task_detail.timer_clear_tooltip": "Stop the timer and remove the card badge",
    "task_detail.timer_elapsed": "Running for {elapsed}",
    "task_detail.due_label": "<b>Due date:</b>",
    "task_detail.due_enable_checkbox": "Enable",
    "task_detail.due_time_checkbox": "Time",
    "task_detail.due_time_tooltip": "Add a time to the due date (creates a calendar reminder)",
    "task_detail.recurrence_none": "No repeat",
    "task_detail.recurrence_daily": "Daily",
    "task_detail.recurrence_weekly": "Weekly",
    "task_detail.recurrence_monthly": "Monthly",
    "task_detail.recurrence_tooltip": "Repeat the task: when the date passes, it advances on its own",
    "task_detail.tags_label": "<b>Tags:</b>",
    "task_detail.assign_tag_btn": "Assign tag",
    "task_detail.manage_tags_btn": "Manage",
    "task_detail.manage_tags_tooltip": "Define permanent tags and their values",
    "task_detail.priority_label": "<b>Priority:</b>",
    "task_detail.priority_tooltip": "Quick task priority (shows as a tag on the board)",
    "task_detail.priority_category_name": "Priority",
    "task_detail.priority_none": "— No priority —",
    "task_detail.priority_low": "Low",
    "task_detail.priority_medium": "Medium",
    "task_detail.priority_high": "High",
    "task_detail.linked_board_label": "<b>Linked board:</b>",
    "task_detail.linked_board_tooltip": "Link this task to another board (shows as a clickable pill on the card)",
    "task_detail.linked_board_none": "— Not linked —",
    "task_detail.links_label": "<b>Links / attachments:</b>",
    "task_detail.link_url_placeholder": "URL or path…",
    "task_detail.link_label_placeholder": "Name (optional)",
    "task_detail.add_link_tooltip": "Add link",
    "task_detail.browse_file_tooltip": "Browse a local file on the PC to attach",
    "task_detail.browse_file_title": "Select a file to attach",
    "task_detail.link_missing_tooltip": "File not found: {path}",
    "task_detail.link_open_failed_title": "Could not open",
    "task_detail.link_open_failed_msg": (
        "Could not open the link or attachment. It may have been moved or deleted."
    ),
    "task_detail.delete_task_btn": "Delete task",
    "task_detail.save_btn": "Save changes",
    "task_detail.close_btn": "Close",
    "task_detail.log_header": "Journal",
    "task_detail.entries_count": "{count} entries",
    "task_detail.notes_kicker": "NOTES",
    "task_detail.saves_hint": "Changes save as you type",
    "task_detail.kicker": "{board} · {column}",
    "task_detail.log_input_placeholder": "Log what you just did… (Ctrl+Enter)",
    "task_detail.add_log_btn": "Add entry",
    "task_detail.load_error_title": "Error",
    "task_detail.load_error_body": "Could not load the task.",
    "task_detail.no_tags_hint": "No tags. Click «Assign tag».",
    "task_detail.tag_pill_tooltip": "Click to change the value",
    "task_detail.tag_pill_remove_tooltip": "Remove from the task",
    "task_detail.warn_title": "Heads up",
    "task_detail.warn_empty_title": "The task title can't be empty.",
    "task_detail.delete_task_title": "Confirm deletion",
    "task_detail.delete_task_body": (
        "Delete this task permanently? Ctrl + Z restores it."
    ),
    "task_detail.no_links_hint": "No links.",
    "task_detail.delete_link_tooltip": "Delete link",
    "task_detail.delete_log_title": "Delete entry",
    "task_detail.delete_log_body": "Delete this journal entry?",

    # --- board_sync / sincronización con Cloud (Google Drive, Dropbox, OneDrive, red) ---
    "sync.link_btn": "Link to Cloud",
    "sync.link_tooltip": "Link this board to Google Drive, Dropbox, OneDrive or a shared folder (.ekboard)",
    "sync.info_dialog_title": "Link board to Cloud",
    "sync.info_header": "Cloud sync with Ekin",
    "sync.info_subtitle": "Collaborate in real time with Google Drive, Dropbox, OneDrive or local network folders.",
    "sync.info_desc": (
        "Ekin syncs this board by generating a single shared file (.ekboard). "
        "Any change you or your team make is detected and merged automatically "
        "in the background by a reactive, No-Data-Loss engine."
    ),
    "sync.info_providers_title": "Instructions by cloud provider:",
    "sync.info_gdrive": (
        "<b>Google Drive</b>: Save the file inside your Google Drive folder synced on this "
        "PC (e.g. <i>G:\\My Drive\\...</i> or <i>C:\\Users\\...\\Google Drive</i>)."
    ),
    "sync.info_dropbox": (
        "<b>Dropbox</b>: Save the file in your synced Dropbox folder (e.g. <i>C:\\Users\\...\\Dropbox</i>)."
    ),
    "sync.info_onedrive": (
        "<b>OneDrive</b>: Save the file in your OneDrive folder (e.g. <i>C:\\Users\\...\\OneDrive</i>)."
    ),
    "sync.info_other": (
        "<b>Other clouds or local network</b>: Also compatible with Nextcloud, Syncthing or any "
        "shared local network (SMB) folder."
    ),
    "sync.info_continue_btn": "Continue and select folder…",
    "sync.info_cancel_btn": "Cancel",
    "sync.synced_badge": "Synced",
    "sync.syncing": "Syncing…",
    "sync.offline_badge": "Local board (not synced)",
    "sync.menu_sync_now": "Sync now",
    "sync.menu_open_location": "Open file location…",
    "sync.menu_unlink": "Unlink sync",
    "sync.dialog_title_link": "Select or create a shared board file",
    "sync.dialog_filter": "Ekin board (*.ekboard);;All files (*.*)",
    "sync.unlink_confirm_title": "Unlink sync",
    "sync.unlink_confirm_body": "Unlink this board from the shared file? The board keeps working locally without affecting other users.",
    "sync.success_title": "Sync successful",
    "sync.error_title": "Sync error",
    "sync.conflict_merged_toast": "Concurrent changes were merged with no data loss.",

    # --- ai_spec / selección múltiple e IA local ---
    "ai_spec.selection_count": "{count} task(s) selected",
    "ai_spec.generate_spec_btn": "Generate with local AI",
    "ai_spec.clear_selection_btn": "Clear",
    "ai_spec.dialog_title": "AI spec generator for agents",
    "ai_spec.mode_label": "Spec mode:",
    "ai_spec.model_label": "Model (Ollama):",
    "ai_spec.refresh_models_tooltip": "Scan active Ollama models (localhost:11434)",
    "ai_spec.mode_coding_agent": "Architecture & code plan (Antigravity / Claude Code / Cursor)",
    "ai_spec.mode_user_stories": "User stories & acceptance criteria (Gherkin)",
    "ai_spec.mode_qa_plan": "Test plan & QA matrix",
    "ai_spec.generate_btn": "Generate SPEC",
    "ai_spec.copy_btn": "Copy SPEC",
    "ai_spec.save_btn": "Save file…",
    "ai_spec.create_task_btn": "Create as task on the board",
    "ai_spec.model_status_label": "AI engine:",
    "ai_spec.status_ready": "Ready to generate",
    "ai_spec.status_generating": "Generating spec with local AI…",
    "ai_spec.copied_toast": "SPEC copied to clipboard!",
    "ai_spec.saved_toast": "Spec saved successfully.",
    "ai_spec.task_created_toast": "Task created on the board with the spec.",
    "ai_spec.download_model_title": "Download autonomous local AI model",
    "ai_spec.download_model_prompt": (
        "Ekin can run an autonomous local AI model (Qwen 2.5 Coder 1.5B, ~980 MB) "
        "with no extra software and without sending your data to the cloud.\n\n"
        "Download the model now?"
    ),
}


def t(key, **kwargs):
    """Devuelve la cadena asociada a `key`, interpolando **kwargs si se pasan."""
    text = STRINGS[key]
    return text.format(**kwargs) if kwargs else text
