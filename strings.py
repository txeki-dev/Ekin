"""Interface strings, centralized for full bilingual support (English & Spanish).

Usage: `from strings import t` and `t("dotted.key")`, or `t("key", name=value)` for the
ones that interpolate (uses `str.format`).
"""

DEFAULT_LANGUAGE = "en"
_CURRENT_LANGUAGE = "en"

LANGUAGES = {
    "en": "English",
    "es": "Español",
}

STRINGS_EN = {
    'main.window_title': 'Ekin v{version}',
    'main.tray.tooltip': 'Ekin Kanban',
    'main.tray.open': 'Open Ekin',
    'main.tray.quit': 'Quit',
    'main.tray.due_today_title': 'Ekin — {count} task(s) due today',
    'main.update.available_title': 'Update available',
    'main.update.available_body': (
        'A new version of Ekin Kanban is available on GitHub.\n'
        'Do you want to download it and restart the app now?'
    ),
    'main.update.done_title': 'Updated',
    'main.update.done_body': 'The app updated successfully. It will restart now.',
    'main.update.dirty_title': 'Update available',
    'main.update.dirty_body': "A new version is available, but there are uncommitted local changes in the app folder. The automatic update was skipped to protect your data — please update manually with 'git pull'.",
    'main.update.failed_title': 'Update failed',
    'main.update.failed_body': "The update could not be applied automatically. Your data is untouched — please update manually with 'git pull'.",
    'main.update.release_available_body': 'A new version of Ekin (v{version}) is available.\n\nDo you want to download and install it now?',
    'main.update.downloading': 'Downloading update...',
    'main.update.download_failed': 'Failed to download update installer. You can download it manually from GitHub.',
    'main.onboarding.board_name': 'My First Board',
    'main.onboarding.col_todo': 'To do',
    'main.onboarding.col_doing': 'In progress',
    'main.onboarding.col_done': 'Done',
    'main.onboarding.task_title': 'Explore Ekin Kanban',
    'main.onboarding.task_description': (
        'Welcome!\n'
        '\n'
        'This is a task card. Click it to:\n'
        '- Change the title\n'
        '- Add a description\n'
        '- Set custom tags\n'
        '- Log your progress in the personal Journal (on the right)'
    ),
    'main.onboarding.tag_category': 'Priority',
    'main.onboarding.tag_value': 'High',
    'main.onboarding.log_entry': 'Initialized the app for the first time. All set to start working!',
    'board_view.column_edit.new_title': 'New column',
    'board_view.column_edit.edit_title': 'Edit column',
    'board_view.column_edit.name_label': '<b>Column name:</b>',
    'board_view.column_edit.name_placeholder': 'e.g. Inbox, In progress...',
    'board_view.column_edit.color_label': '<b>Accent color:</b>',
    'board_view.column_edit.color_dialog_title': 'Select column color',
    'board_view.column_edit.save': 'Save',
    'board_view.column_edit.cancel': 'Cancel',
    'board_view.column_edit.warn_title': 'Heads up',
    'board_view.column_edit.warn_empty_name': "The column name can't be empty.",
    'board_view.board_selection.target_label': '<b>Select the destination board:</b>',
    'board_view.board_selection.cancel': 'Cancel',
    'board_view.board_selection.no_other_boards': 'No other boards',
    'board_view.header.toggle_sidebar_tooltip': 'Show/hide sidebar',
    'board_view.header.default_title': 'My Board',
    'board_view.header.counts': '{tasks} tasks · {due} due this week',
    'board_view.welcome': (
        'Welcome to Ekin Kanban!\n'
        '\n'
        'Create your first board in the sidebar\n'
        'to start organizing your tasks and journals.'
    ),
    'board_view.add_column_btn': 'New column',
    'board_view.delete_column.title': 'Delete column',
    'board_view.delete_column.body': (
        "Delete the column '{name}'?\n"
        'Its tasks, their journals and links go with it. Ctrl + Z restores the whole column.'
    ),
    'board_view.delete_column.undo_label': 'Delete column',
    'board_view.copy_column.title': 'Copy column',
    'board_view.copy_column.action': 'Copy',
    'board_view.copy_column.fallback_board_name': 'the selected board',
    'board_view.copy_column.done_title': 'Column copied',
    'board_view.copy_column.done_body': "The column '{column}' and all its tasks/logs were copied to '{board}'.",
    'board_view.add_task.title': 'New task',
    'board_view.add_task.prompt': 'Enter the task title:',
    'board_view.delete_task.undo_label': 'Delete task',
    'widgets.card.board_link_tooltip': 'Go to linked board',
    'widgets.column.collapse_tooltip': 'Collapse column',
    'widgets.column.expand_tooltip': 'Expand column',
    'widgets.column.edit_tooltip': 'Edit column (options: edit, copy, delete)',
    'widgets.column.title_drag_tooltip': 'Drag to reorder or move this column to another board',
    'widgets.column.task_count_tooltip': '{count} task(s)',
    'widgets.column.add_task_btn': 'Add task',
    'widgets.column.menu_edit': 'Edit column',
    'widgets.column.menu_copy': 'Copy to another board...',
    'widgets.column.menu_delete': 'Delete column',
    'sidebar.title': 'EKIN',
    'sidebar.boards_subtitle': 'Boards',
    'sidebar.add_board_btn': 'New board',
    'sidebar.edit_board_btn': 'Edit',
    'sidebar.copy_board_btn': 'Copy',
    'sidebar.delete_board_btn': 'Delete',
    'sidebar.archived_btn': 'Archived boards',
    'sidebar.archived_tooltip': 'Show/hide archived boards (right-click a board to archive)',
    'sidebar.export_btn': 'Export',
    'sidebar.export_tooltip': 'Export boards to JSON, CSV or Markdown',
    'sidebar.import_btn': 'Import',
    'sidebar.import_tooltip': 'Import boards, columns and tasks from a JSON file',
    'sidebar.board_config_tooltip': 'Board options',
    'sidebar.board_config.title': 'Board options',
    'sidebar.bell_tooltip': 'Overdue tasks or due today/tomorrow',
    'sidebar.search_tooltip': 'Search tasks (Ctrl+F)',
    'sidebar.calendar_tooltip': 'Open calendar view',
    'sidebar.settings_tooltip': 'Settings (theme, notifications)',
    'sidebar.shortcuts_tooltip': 'Keyboard shortcuts (Ctrl+/)',
    'sidebar.notifications.header': 'Due soon',
    'sidebar.notifications.empty': 'No overdue or upcoming tasks.',
    'sidebar.notifications.group_overdue': 'OVERDUE',
    'sidebar.notifications.group_today': 'TODAY',
    'sidebar.notifications.group_tomorrow': 'TOMORROW',
    'sidebar.notifications.item_no_title': '(untitled)',
    'sidebar.notifications.item_tooltip': '{board} · due {due_date}',
    'sidebar.board_button.archived_tooltip': 'Archived board — right-click to unarchive',
    'sidebar.board_button.menu_unarchive': 'Unarchive board',
    'sidebar.board_button.menu_archive': 'Archive board',
    'sidebar.board_edit.new_title': 'New board',
    'sidebar.board_edit.edit_title': 'Edit board',
    'sidebar.board_edit.copy_title': 'Copy board',
    'sidebar.board_edit.copy_default_name': '{name} - Copy',
    'sidebar.board_edit.name_label': '<b>Board name:</b>',
    'sidebar.board_edit.name_placeholder': 'e.g. Work, Personal, Trip...',
    'sidebar.board_edit.color_label': '<b>Board color:</b>',
    'sidebar.board_edit.color_dialog_title': 'Select board color',
    'sidebar.board_edit.save': 'Save',
    'sidebar.board_edit.cancel': 'Cancel',
    'sidebar.board_edit.warn_title': 'Heads up',
    'sidebar.board_edit.warn_empty_name': "The board name can't be empty.",
    'sidebar.export_menu.json': 'JSON (.json)',
    'sidebar.export_menu.csv': 'Tasks CSV (.csv)',
    'sidebar.export_menu.markdown': 'Markdown report (.md)',
    'sidebar.export.dialog_title': 'Export {label}',
    'sidebar.export.error_title': 'Export error',
    'sidebar.export.error_body': (
        'Could not export:\n'
        '{error}'
    ),
    'sidebar.export.done_title': 'Exported',
    'sidebar.export.done_body': (
        '{label} export saved to:\n'
        '{path}'
    ),
    'sidebar.delete_board.title': 'Delete board',
    'sidebar.delete_board.body': (
        "Delete the board '{name}'?\n"
        'All its columns, tasks and journals go with it permanently.'
    ),
    'sidebar.delete_board.undo_label': 'Delete board',
    'export_dialog.window_title': 'Export boards',
    'export_dialog.scope_group': '<b>Export scope:</b>',
    'export_dialog.scope_all': 'All boards (including archived)',
    'export_dialog.scope_current': 'Only the active board: «{name}»',
    'export_dialog.format_group': '<b>File format:</b>',
    'export_dialog.format_json': 'JSON (.json) — Full data or templates',
    'export_dialog.json_include_tasks': 'Include tasks, tags, links and journal',
    'export_dialog.json_template_hint': 'If unchecked, only the column structure is exported as a reusable template.',
    'export_dialog.format_csv': 'CSV (.csv) — Task list for spreadsheets (Excel / Sheets)',
    'export_dialog.format_markdown': 'Markdown (.md) — Readable project report',
    'export_dialog.md_include_details': 'Include descriptions, links and journal in the report',
    'export_dialog.export_btn': 'Export to file...',
    'export_dialog.cancel_btn': 'Cancel',
    'export_dialog.save_title': 'Save export file',
    'export_dialog.done_title': 'Export complete',
    'export_dialog.done_body': (
        '{label} export saved successfully to:\n'
        '{path}'
    ),
    'export_dialog.error_title': 'Export error',
    'export_dialog.error_body': (
        'Could not complete the export:\n'
        '{error}'
    ),
    'import_dialog.window_title': 'Import boards from JSON',
    'import_dialog.open_title': 'Select a JSON file to import',
    'import_dialog.file_label': '<b>File:</b> {filename}',
    'import_dialog.summary_label': 'Detected <b>{boards}</b> board(s), <b>{columns}</b> column(s) and <b>{tasks}</b> task(s).',
    'import_dialog.options_group': '<b>Import options:</b>',
    'import_dialog.opt_full': 'Import everything (boards, columns, tasks, tags, links and journal)',
    'import_dialog.opt_structure_only': 'Import only the column structure (as a template without tasks)',
    'import_dialog.template_only_hint': 'This file contains only column structure (a template).',
    'import_dialog.import_btn': 'Import to Ekin',
    'import_dialog.cancel_btn': 'Cancel',
    'import_dialog.done_title': 'Import complete',
    'import_dialog.done_body': 'Imported {count} board(s) successfully.',
    'import_dialog.error_title': 'Import error',
    'import_dialog.error_body': (
        'Could not import the file:\n'
        '{error}'
    ),
    'calendar.chip_no_title': '(untitled)',
    'calendar.chip_tooltip': (
        '{board} · {title}\n'
        'Drag to another day to reschedule'
    ),
    'calendar.more_tasks': '+{count} more',
    'calendar.today_btn': 'Today',
    'calendar.mode_month': 'Month',
    'calendar.mode_week': 'Week',
    'calendar.mode_day': 'Day',
    'calendar.mode_tooltip': 'Calendar view',
    'calendar.board_filter_tooltip': 'Filter by board',
    'calendar.settings_btn': 'Settings',
    'calendar.settings_tooltip': 'Sync / export to Google, Apple or Outlook',
    'calendar.close_btn': 'Back to board',
    'calendar.close_tooltip': 'Back to the board view',
    'calendar.all_boards': 'All boards',
    'calendar.week_period': 'Week {start} – {end}',
    'calendar.error_title': 'Error',
    'calendar.settings_dialog.title': 'Calendar settings',
    'calendar.settings_dialog.header': '<b>Calendar sync</b>',
    'calendar.settings_dialog.info': 'Ekin exports your tasks with a due date to a standard <b>iCalendar (.ics)</b> file, compatible with Google Calendar, Apple Calendar and Outlook.',
    'calendar.settings_dialog.sync_title': '<b>Automatic sync</b> (recommended)',
    'calendar.settings_dialog.sync_desc': 'Ekin keeps a .ics file <b>always up to date</b> (rewriting it whenever tasks change). Save it in a Dropbox / OneDrive / Google Drive folder and <b>subscribe</b> to it once: from then on it updates itself.',
    'calendar.settings_dialog.sync_board_tooltip': 'Automatically sync all boards or just one',
    'calendar.settings_dialog.configure_btn_initial': 'Choose file…',
    'calendar.settings_dialog.configure_btn_change': 'Change file…',
    'calendar.settings_dialog.disable_btn': 'Disable',
    'calendar.settings_dialog.subscribe_title': '<b>Subscribe in your calendar</b>',
    'calendar.settings_dialog.subscribe_desc': "Upload the .ics file to a public folder (Google Drive / Dropbox / OneDrive) and paste its <b>public URL</b> here. Ekin saves it and, depending on the button, copies it to the clipboard and opens the provider's page to <b>add a calendar by URL</b> (the manual step that often fails). Detailed guide below.",
    'calendar.settings_dialog.public_url_placeholder': 'https://…/ekin_calendario.ics',
    'calendar.settings_dialog.google_btn_tooltip': "Copy the URL and open Google Calendar's «Add by URL»",
    'calendar.settings_dialog.outlook_btn_tooltip': "Copy the URL and open Outlook's «Subscribe from web»",
    'calendar.settings_dialog.apple_btn_tooltip': 'Copy the URL as a webcal:// link for iPhone/Mac',
    'calendar.export_once_btn': 'Export a copy…',
    'calendar.export_once_tooltip': 'Save a one-off .ics snapshot to another location',
    'calendar.export_board_tooltip': 'Export the calendar of all boards or just one',
    'calendar.settings_dialog.close_btn': 'Close',
    'calendar.settings_dialog.sync_active': 'Syncing to:<br><code>{path}</code>',
    'calendar.settings_dialog.sync_inactive': 'Automatic sync disabled.',
    'calendar.settings_dialog.configure_file_dialog_title': 'Sync file',
    'calendar.settings_dialog.configure_error_body': (
        'Could not create the file:\n'
        '{error}'
    ),
    'calendar.settings_dialog.sync_activated_title': 'Sync enabled',
    'calendar.settings_dialog.sync_activated_body': (
        'Ekin will keep {count} task(s) synced at:\n'
        '{path}\n'
        '\n'
        'Subscribe to this file once from your calendar and it will update itself.'
    ),
    'calendar.settings_dialog.empty_url_title': 'Empty URL',
    'calendar.settings_dialog.empty_url_body': 'Paste the public URL of your .ics file first (the shared link of the cloud folder where you sync it).',
    'calendar.settings_dialog.google_title': 'Google Calendar',
    'calendar.settings_dialog.google_body': (
        "I copied the URL to the clipboard and opened Google Calendar (on the computer; the mobile app can't add by URL).\n"
        '\n'
        '1. Left side menu → «Other calendars» → «+» → «From URL».\n'
        '2. Paste the URL (Ctrl+V) and click «Add calendar».\n'
        '\n'
        "Note: Google reloads URL calendars slowly (every few hours, up to ~24 h) and it can't be forced."
    ),
    'calendar.settings_dialog.outlook_title': 'Outlook Calendar',
    'calendar.settings_dialog.outlook_body': (
        'I copied the URL to the clipboard and opened Outlook in the browser.\n'
        '\n'
        '1. In Outlook.com: «Add calendar» → «Subscribe from web».\n'
        '   (In work/Microsoft 365 Outlook the path is outlook.office.com → same option.)\n'
        '2. Paste the URL (Ctrl+V), give it a name and color, and click «Import»/«Subscribe».\n'
        '\n'
        'Desktop Outlook (classic) also supports: Home → «Open calendar» → «From Internet…» and paste the URL.'
    ),
    'calendar.settings_dialog.apple_title': 'Apple / iCloud',
    'calendar.settings_dialog.apple_body': (
        'I copied the URL as a <b>webcal://</b> link to the clipboard (so iOS/macOS recognize it as a subscription). Paste it here:\n'
        '\n'
        '• iPhone/iPad: Settings → Calendar → Accounts → Add account → Other → «Add subscribed calendar» → paste the link → Next.\n'
        '• Mac (Calendar app): File → «New calendar subscription…» → paste the link → Subscribe; there you can set the refresh frequency (even every few minutes).\n'
        '\n'
        'The subscription is saved in iCloud and shows on all your Apple devices.'
    ),
    'calendar.settings_dialog.provider_guide': "<b>How to subscribe (stays in sync, no duplicates)</b><p><b>0) Get a public, direct URL to the .ics.</b> Save the file in a cloud folder and share the link <i>directly to the file</i> (not to a preview page):<ul><li><b>Google Drive</b>: share as «Anyone with the link». The normal link points to an HTML view; use the direct-download form <code>https://drive.google.com/uc?export=download&id=FILE_ID</code>.</li><li><b>Dropbox</b>: copy the link and change the trailing <code>?dl=0</code> to <code>?dl=1</code>.</li><li><b>OneDrive</b>: «Share» → «Anyone with the link» → copy the link.</li></ul>Open it in an incognito window: you should see text starting with <code>BEGIN:VCALENDAR</code>. If you see a login or a preview, the link won't work.</p><p><b>Google Calendar</b> (computer only): side menu → «Other calendars» → «+» → «From URL» → paste the URL → «Add calendar». Slow refresh (several hours).</p><p><b>Outlook</b>: in <i>Outlook.com/365 (web)</i> → «Add calendar» → «Subscribe from web» → paste the URL → name/color → «Import». In <i>desktop Outlook</i> → Home → «Open calendar» → «From Internet…» → paste the URL.</p><p><b>Apple / iCloud</b> (use a <code>webcal://</code> link): <i>iPhone/iPad</i> → Settings → Calendar → Accounts → Add account → Other → «Add subscribed calendar» → paste the link. <i>Mac</i> → Calendar app → File → «New calendar subscription…» → paste the link (you can choose how often it updates).</p><p><b>Subscribe ≠ Import.</b> «Import» a copy is a fixed snapshot: it doesn't reflect changes or deletions and may duplicate events. Subscribe to the URL so it updates itself.</p>",
    'calendar.export_dialog_title': 'Export a calendar copy',
    'calendar.export_error_body': (
        'Could not export the calendar:\n'
        '{error}'
    ),
    'calendar.export_done_title': 'Exported',
    'calendar.export_done_body': (
        'Exported {count} dated task(s) to:\n'
        '{path}\n'
        '\n'
        'Remember: an imported copy is a fixed snapshot; to keep it up to date, use the automatic sync above and subscribe to the file.'
    ),
    'search.window_title': 'Search tasks',
    'search.header': '<b>Search tasks</b>',
    'search.text_placeholder': 'Title or description…',
    'search.all_boards': 'All boards',
    'search.all_tags': 'All tags',
    'search.only_due_checkbox': 'Only with a due date',
    'search.close_btn': 'Close',
    'search.result_count': '{count} result(s)',
    'search.no_results': 'No results.',
    'search.result_no_title': '(untitled)',
    'search.result_tooltip': '{board} · {column}',
    'settings.window_title': 'Settings',
    'settings.header': 'Settings',
    'settings.theme_label': 'Theme',
    'settings.theme_dark': 'Dark',
    'settings.theme_light': 'Light',
    'settings.theme_desc': 'Applies immediately — no restart.',
    'settings.notifications_label': 'Windows notifications for tasks due today',
    'settings.notifications_checkbox': 'Show Windows alerts for tasks due today',
    'settings.notifications_desc': 'One summary when Ekin starts, then once a day.',
    'settings.timer_alert_label': 'Warn on the card when a timer runs longer than',
    'settings.timer_alert_suffix': ' h',
    'settings.timer_alert_desc': 'Stale tasks turn terracotta on the board.',
    'settings.geometry_hint': 'The window size and position are remembered automatically.',
    'settings.close_btn': 'Close',
    'shortcuts.window_title': 'Keyboard shortcuts',
    'shortcuts.header': '<b>Keyboard shortcuts</b>',
    'shortcuts.section_general': 'General & navigation',
    'shortcuts.section_editor': 'Rich text — notes & journal',
    'shortcuts.item_search': 'Ctrl+F — Global search',
    'shortcuts.item_new_task': 'Ctrl+N — New task in the last column you interacted with (if none, the first column of the active board); inside the text editor, Ctrl+N is Bold',
    'shortcuts.item_new_column': 'Ctrl+Shift+N — New column in the active board',
    'shortcuts.item_prev_next_board': 'Alt+↑ / Alt+↓ — Previous / next board',
    'shortcuts.item_jump_board': 'Ctrl+1 … Ctrl+9 — Jump straight to board № in the sidebar',
    'shortcuts.item_calendar': 'Ctrl+Shift+C — Open the calendar',
    'shortcuts.item_settings': 'Ctrl+, — Open Settings',
    'shortcuts.item_shortcuts': 'Ctrl+/ — Show this window',
    'shortcuts.item_undo_redo': 'Ctrl+Z / Ctrl+Y (or Ctrl+Shift+Z) — Undo / redo',
    'shortcuts.item_close_dialog': 'Esc — Close the open dialog',
    'shortcuts.item_bold': 'Ctrl+B or Ctrl+N — Bold (inside the editor)',
    'shortcuts.item_italic': 'Ctrl+K or Ctrl+I — Italic (inside the editor)',
    'shortcuts.item_strike': 'Ctrl+Shift+X — Strikethrough (inside the editor)',
    'shortcuts.item_align': 'Ctrl+L / Ctrl+E / Ctrl+R / Ctrl+J — Align text (left, center, right, justify)',
    'shortcuts.item_case': 'Ctrl+Shift+U / Ctrl+Shift+L / Shift+F3 — UPPERCASE / lowercase',
    'shortcuts.item_nest_bullet': 'Tab (on a bullet) — Nest the bullet (inside the editor)',
    'shortcuts.item_quote': 'Ctrl+Shift+Q or typing «> » — Quote / callout block (inside the editor)',
    'shortcuts.item_paste_plain': 'Ctrl+Shift+V — Paste as plain text (inside the editor)',
    'shortcuts.item_arrow': 'Typing «-->» becomes → automatically (inside the editor)',
    'shortcuts.item_add_log': 'Ctrl+Enter — Add the note to the journal (task detail)',
    'shortcuts.hint': 'Press Ctrl+/ anytime to see this window again.',
    'shortcuts.close_btn': 'Close',
    'markdown_edit.bold_tooltip': 'Bold (Ctrl+B or Ctrl+N)',
    'markdown_edit.italic_tooltip': 'Italic (Ctrl+K or Ctrl+I)',
    'markdown_edit.strike_tooltip': 'Strikethrough (Ctrl+Shift+X)',
    'markdown_edit.align_left_tooltip': 'Align left (Ctrl+L)',
    'markdown_edit.align_center_tooltip': 'Center text (Ctrl+E)',
    'markdown_edit.align_right_tooltip': 'Align right (Ctrl+R)',
    'markdown_edit.align_justify_tooltip': 'Justify text (Ctrl+J)',
    'markdown_edit.upper_tooltip': 'Convert to UPPERCASE (Ctrl+Shift+U)',
    'markdown_edit.lower_tooltip': 'Convert to lowercase (Ctrl+Shift+L)',
    'markdown_edit.context_upper': 'Convert to UPPERCASE',
    'markdown_edit.context_lower': 'Convert to lowercase',
    'markdown_edit.bullet_tooltip': 'Bulleted list  ·  also with «* », «- » or «+ »',
    'markdown_edit.hr_tooltip': 'Horizontal rule  ·  also by typing «---»',
    'markdown_edit.arrow_tooltip': 'Insert arrow (→)  ·  also by typing «-->»',
    'markdown_edit.color_tooltip': 'Text color',
    'markdown_edit.color_default': 'Default color',
    'markdown_edit.color_more': 'More colors…',
    'markdown_edit.color_dialog_title': 'Select text color',
    'markdown_edit.table_tooltip': 'Insert table',
    'markdown_edit.table_dialog_title': 'Insert table',
    'markdown_edit.table_rows_label': 'Rows:',
    'markdown_edit.table_cols_label': 'Columns:',
    'markdown_edit.code_tooltip': 'Insert code block  ·  also with «```»',
    'markdown_edit.code_dialog_title': 'Insert code block',
    'markdown_edit.code_lang_label': 'Programming language:',
    'markdown_edit.code_text_label': 'Code:',
    'markdown_edit.code_insert_btn': 'Insert',
    'markdown_edit.code_cancel_btn': 'Cancel',
    'markdown_edit.quote_tooltip': "Quote / callout block (Ctrl+Shift+Q, or type '> ' at start)",
    'markdown_edit.quote_placeholder': 'Type a quote...',
    'markdown_edit.paste_plain_menu': 'Paste plain text (Ctrl+Shift+V)',
    'markdown_edit.paste_formatted_menu': 'Paste with formatting',
    'markdown_edit.image_size_menu': 'Image size',
    'markdown_edit.image_size_25': '25% width',
    'markdown_edit.image_size_50': '50% width',
    'markdown_edit.image_size_75': '75% width',
    'markdown_edit.image_size_100': '100% width (fit editor)',
    'markdown_edit.image_size_custom': 'Custom width (px)…',
    'markdown_edit.image_size_dialog_title': 'Resize image',
    'markdown_edit.image_size_dialog_label': 'Image width in pixels:',
    'markdown_edit.delete_code_btn': 'Delete',
    'markdown_edit.delete_code_tooltip': 'Delete this code block',
    'markdown_edit.delete_code_btn_menu': 'Delete code block',
    'markdown_edit.link_tooltip': 'Insert web link (URL)',
    'markdown_edit.link_dialog_title': 'Insert link',
    'markdown_edit.link_url_label': 'Web address (URL):',
    'markdown_edit.link_text_label': 'Display text (optional):',
    'markdown_edit.link_insert_btn': 'Insert',
    'markdown_edit.link_cancel_btn': 'Cancel',
    'log_entry.edit_tooltip': 'Edit comment',
    'log_entry.delete_tooltip': 'Delete comment',
    'log_entry.save_btn': 'Save',
    'log_entry.cancel_btn': 'Cancel',
    'image_preview.window_title': 'Image preview',
    'tag_manager.window_title': 'Manage tags',
    'tag_manager.header': '<b>Tags</b>',
    'tag_manager.add_category_btn': 'New',
    'tag_manager.category_action_label': 'Rename tag',
    'tag_manager.delete_category_tooltip': 'Delete tag',
    'tag_manager.values_title_default': '<b>Values</b>',
    'tag_manager.values_title_for_category': '<b>Values of «{category}»</b>',
    'tag_manager.new_value_placeholder': 'New value (e.g. High)…',
    'tag_manager.new_value_color_tooltip': 'Color of the new value',
    'tag_manager.add_value_btn': 'Add value',
    'tag_manager.close_btn': 'Close',
    'tag_manager.add_category_dialog_title': 'New tag',
    'tag_manager.add_category_prompt': 'Tag name (e.g. Priority):',
    'tag_manager.new_name_prompt': 'New name:',
    'tag_manager.delete_category_body': (
        'Delete the tag «{category}» and all its values?\n'
        'It will be removed from every task that uses it.'
    ),
    'tag_manager.no_category_hint': 'Create or select a tag on the left to define its values.',
    'tag_manager.no_values_hint': 'No values yet. Add the first one below.',
    'tag_manager.swatch_tooltip': 'Change color',
    'tag_manager.rename_value_tooltip': 'Rename value',
    'tag_manager.delete_value_tooltip': 'Delete value',
    'tag_manager.color_dialog_title': 'Value color',
    'tag_manager.warn_title': 'Heads up',
    'tag_manager.duplicate_value_body': 'A value with that name already exists in this tag.',
    'tag_manager.delete_value_body': (
        'Delete the value «{value}»?\n'
        "It will be removed from the tasks it's assigned to."
    ),
    'tag_picker.title_edit': 'Edit tag',
    'tag_picker.title_assign': 'Assign tag',
    'tag_picker.category_label': '<b>Tag</b>',
    'tag_picker.value_label': '<b>Value</b>',
    'tag_picker.manage_btn': 'Manage tags…',
    'tag_picker.accept_btn': 'OK',
    'tag_picker.cancel_btn': 'Cancel',
    'tag_picker.none_option': '— None (hide) —',
    'tag_picker.no_categories_hint': 'No tags defined. Use «Manage tags…» to create one.',
    'tag_picker.no_values_hint': 'This tag has no values. Add them in «Manage tags…».',
    'tag_picker.warn_title': 'Heads up',
    'tag_picker.warn_no_category': 'Create a tag first in «Manage tags…».',
    'tag_picker.warn_no_value': 'Select a value (or create it in «Manage tags…»).',
    'task_detail.window_title': 'Task details',
    'task_detail.title_label': '<b>Task title</b>',
    'task_detail.title_placeholder': 'e.g. Write the monthly report...',
    'task_detail.description_label': '<b>Description / Notes</b>',
    'task_detail.description_placeholder': 'Add details about this task...',
    'task_detail.timer_label': '<b>Timer:</b>',
    'task_detail.timer_start_btn': 'Start',
    'task_detail.timer_restart_btn': 'Restart',
    'task_detail.timer_clear_btn': 'Stop',
    'task_detail.timer_clear_tooltip': 'Stop the timer and remove the card badge',
    'task_detail.timer_elapsed': 'Running for {elapsed}',
    'task_detail.due_label': '<b>Due date:</b>',
    'task_detail.due_enable_checkbox': 'Enable',
    'task_detail.due_time_checkbox': 'Time',
    'task_detail.due_time_tooltip': 'Add a time to the due date (creates a calendar reminder)',
    'task_detail.recurrence_none': 'No repeat',
    'task_detail.recurrence_daily': 'Daily',
    'task_detail.recurrence_weekly': 'Weekly',
    'task_detail.recurrence_monthly': 'Monthly',
    'task_detail.recurrence_tooltip': 'Repeat the task: when the date passes, it advances on its own',
    'task_detail.tags_label': '<b>Tags:</b>',
    'task_detail.assign_tag_btn': 'Assign tag',
    'task_detail.manage_tags_btn': 'Manage',
    'task_detail.manage_tags_tooltip': 'Define permanent tags and their values',
    'task_detail.priority_label': '<b>Priority:</b>',
    'task_detail.priority_tooltip': 'Quick task priority (shows as a tag on the board)',
    'task_detail.priority_category_name': 'Priority',
    'task_detail.priority_none': '— No priority —',
    'task_detail.priority_low': 'Low',
    'task_detail.priority_medium': 'Medium',
    'task_detail.priority_high': 'High',
    'task_detail.linked_board_label': '<b>Linked board:</b>',
    'task_detail.linked_board_tooltip': 'Link this task to another board (shows as a clickable pill on the card)',
    'task_detail.linked_board_none': '— Not linked —',
    'task_detail.links_label': '<b>Links / attachments:</b>',
    'task_detail.link_url_placeholder': 'URL or path…',
    'task_detail.link_label_placeholder': 'Name (optional)',
    'task_detail.add_link_tooltip': 'Add link',
    'task_detail.browse_file_tooltip': 'Browse a local file on the PC to attach',
    'task_detail.browse_file_title': 'Select a file to attach',
    'task_detail.link_missing_tooltip': 'File not found: {path}',
    'task_detail.link_open_failed_title': 'Could not open',
    'task_detail.link_open_failed_msg': 'Could not open the link or attachment. It may have been moved or deleted.',
    'task_detail.link_security_title': 'Security warning',
    'task_detail.link_security_executable_msg': (
        "'{target}' is an executable program or script ({ext}).\n"
        '\n'
        'Opening executable files from shared or untrusted boards may harm your computer.\n'
        '\n'
        'Are you sure you want to open it?'
    ),
    'task_detail.link_security_unc_msg': (
        "'{target}' is a network share path (UNC).\n"
        '\n'
        'Opening network paths from shared or untrusted boards can expose your network credentials or access remote files.\n'
        '\n'
        'Are you sure you want to open it?'
    ),
    'task_detail.link_security_unc_executable_msg': (
        "'{target}' is an executable program or script on a remote network share ({ext}).\n"
        '\n'
        'Opening remote executables from shared or untrusted boards may harm your computer.\n'
        '\n'
        'Are you sure you want to open it?'
    ),
    'task_detail.link_security_scheme_msg': (
        "'{target}' uses an unrecognized or potentially unsafe protocol ({scheme}).\n"
        '\n'
        'Opening this link may harm your computer.\n'
        '\n'
        'Are you sure you want to open it?'
    ),
    'task_detail.delete_task_btn': 'Delete task',
    'task_detail.save_btn': 'Save changes',
    'task_detail.close_btn': 'Close',
    'task_detail.log_header': 'Journal',
    'task_detail.entries_count': '{count} entries',
    'task_detail.notes_kicker': 'NOTES',
    'task_detail.notes_last_edited': 'Last edited: {timestamp}',
    'task_detail.saves_hint': 'Changes save as you type',
    'task_detail.kicker': '{board} · {column}',
    'task_detail.log_input_placeholder': 'Log what you just did… (Ctrl+Enter)',
    'task_detail.add_log_btn': 'Add entry',
    'task_detail.load_error_title': 'Error',
    'task_detail.load_error_body': 'Could not load the task.',
    'task_detail.no_tags_hint': 'No tags. Click «Assign tag».',
    'task_detail.tag_pill_tooltip': 'Click to change the value',
    'task_detail.tag_pill_remove_tooltip': 'Remove from the task',
    'task_detail.warn_title': 'Heads up',
    'task_detail.warn_empty_title': "The task title can't be empty.",
    'task_detail.delete_task_title': 'Confirm deletion',
    'task_detail.delete_task_body': 'Delete this task permanently? Ctrl + Z restores it.',
    'task_detail.no_links_hint': 'No links.',
    'task_detail.delete_link_tooltip': 'Delete link',
    'task_detail.delete_log_title': 'Delete entry',
    'task_detail.delete_log_body': 'Delete this journal entry?',
    'board_view.bulk_add_btn': 'Bulk add tasks',
    'board_view.bulk_add_tooltip': 'Add multiple tasks at once via table',
    'bulk_add.dialog_title': 'Bulk add tasks',
    'bulk_add.header': '<b>Bulk add tasks</b>',
    'bulk_add.instructions': 'Define multiple tasks in the table below. You can also paste copied rows from Excel or Sheets.',
    'bulk_add.col_title': 'Title *',
    'bulk_add.col_description': 'Description',
    'bulk_add.col_column': 'Column',
    'bulk_add.add_row_btn': 'Add row',
    'bulk_add.del_row_btn': 'Remove row',
    'bulk_add.create_btn': 'Create tasks',
    'bulk_add.cancel_btn': 'Cancel',
    'bulk_add.warn_no_tasks': 'Please enter at least one task with a title.',
    'bulk_add.success_toast': '{count} task(s) created successfully.',
    'sync.menu_open_shared': 'Connect existing .ekboard file…',
    'sync.or_connect_existing_prompt': '— or connect a shared cloud board —',
    'sync.open_shared_title': 'Select existing .ekboard file from Cloud / network',
    'sync.open_shared_success': 'Connected shared board «{name}» successfully.',
    'sync.open_shared_exists': 'This board is already in your boards list.',
    'sync.link_btn': 'Link to Cloud',
    'sync.link_tooltip': 'Link this board to Google Drive, Dropbox, OneDrive or a shared folder (.ekboard)',
    'sync.info_dialog_title': 'Link board to Cloud',
    'sync.info_header': 'Cloud sync with Ekin',
    'sync.info_subtitle': 'Collaborate in real time with Google Drive, Dropbox, OneDrive or local network folders.',
    'sync.info_desc': 'Ekin syncs this board by generating a single shared file (.ekboard). Any change you or your team make is detected and merged automatically in the background by a reactive, No-Data-Loss engine.',
    'sync.info_providers_title': 'Instructions by cloud provider:',
    'sync.info_gdrive': '<b>Google Drive</b>: Save the file inside your Google Drive folder synced on this PC (e.g. <i>G:\\My Drive\\...</i> or <i>C:\\Users\\...\\Google Drive</i>).',
    'sync.info_dropbox': '<b>Dropbox</b>: Save the file in your synced Dropbox folder (e.g. <i>C:\\Users\\...\\Dropbox</i>).',
    'sync.info_onedrive': '<b>OneDrive</b>: Save the file in your OneDrive folder (e.g. <i>C:\\Users\\...\\OneDrive</i>).',
    'sync.info_other': '<b>Other clouds or local network</b>: Also compatible with Nextcloud, Syncthing or any shared local network (SMB) folder.',
    'sync.info_continue_btn': 'Continue and select folder…',
    'sync.info_cancel_btn': 'Cancel',
    'sync.synced_badge': 'Synced',
    'sync.syncing': 'Syncing…',
    'sync.offline_badge': 'Local board (not synced)',
    'sync.menu_sync_now': 'Sync now',
    'sync.menu_open_location': 'Open file location…',
    'sync.menu_unlink': 'Unlink sync',
    'sync.dialog_title_link': 'Select or create a shared board file',
    'sync.dialog_filter': 'Ekin board (*.ekboard);;All files (*.*)',
    'sync.unlink_confirm_title': 'Unlink sync',
    'sync.unlink_confirm_body': 'Unlink this board from the shared file? The board keeps working locally without affecting other users.',
    'sync.success_title': 'Sync successful',
    'sync.error_title': 'Sync error',
    'sync.conflict_merged_toast': 'Concurrent changes were merged with no data loss.',
    'ai_spec.selection_count': '{count} task(s) selected',
    'ai_spec.generate_spec_btn': 'Generate with local AI',
    'ai_spec.clear_selection_btn': 'Clear',
    'ai_spec.dialog_title': 'AI spec generator for agents',
    'ai_spec.mode_label': 'Spec mode:',
    'ai_spec.model_label': 'Model (Ollama):',
    'ai_spec.refresh_models_tooltip': 'Scan active Ollama models (localhost:11434)',
    'ai_spec.mode_coding_agent': 'Architecture & code plan (Antigravity / Claude Code / Cursor)',
    'ai_spec.mode_user_stories': 'User stories & acceptance criteria (Gherkin)',
    'ai_spec.mode_qa_plan': 'Test plan & QA matrix',
    'ai_spec.generate_btn': 'Generate SPEC',
    'ai_spec.copy_btn': 'Copy SPEC',
    'ai_spec.save_btn': 'Save file…',
    'ai_spec.create_task_btn': 'Create as task on the board',
    'ai_spec.model_status_label': 'AI engine:',
    'ai_spec.status_ready': 'Ready to generate',
    'ai_spec.status_generating': 'Generating spec with local AI…',
    'ai_spec.copied_toast': 'SPEC copied to clipboard!',
    'ai_spec.saved_toast': 'Spec saved successfully.',
    'ai_spec.task_created_toast': 'Task created on the board with the spec.',
    'ai_spec.download_model_title': 'Download autonomous local AI model',
    'ai_spec.download_model_prompt': (
        'Ekin can run an autonomous local AI model (Qwen 2.5 Coder 1.5B, ~980 MB) with no extra software and without sending your data to the cloud.\n'
        '\n'
        'Download the model now?'
    ),
    'settings.language_label': 'Language',
    'settings.language_desc': 'Display language · Changes apply immediately.',
    'settings.language_en': 'English',
    'settings.language_es': 'Spanish',
}

STRINGS_ES = {
    'main.window_title': 'Ekin v{version}',
    'main.tray.tooltip': 'Ekin Kanban',
    'main.tray.open': 'Abrir Ekin',
    'main.tray.quit': 'Salir',
    'main.tray.due_today_title': 'Ekin — {count} tarea(s) vencen hoy',
    'main.update.available_title': 'Actualización Disponible',
    'main.update.available_body': (
        'Hay una nueva versión de Ekin Kanban en GitHub.\n'
        '¿Deseas descargarla y reiniciar la aplicación ahora?'
    ),
    'main.update.done_title': 'Actualizado',
    'main.update.done_body': 'La aplicación se ha actualizado con éxito. Se reiniciará ahora.',
    'main.update.dirty_title': 'Actualización disponible',
    'main.update.dirty_body': "Hay una nueva versión disponible, pero hay cambios locales sin confirmar en la carpeta de la aplicación. La actualización automática se ha omitido para proteger tus datos — actualiza manualmente con 'git pull'.",
    'main.update.failed_title': 'Actualización fallida',
    'main.update.failed_body': "La actualización no se pudo aplicar automáticamente. Tus datos están intactos — actualiza manualmente con 'git pull'.",
    'main.update.release_available_body': 'Hay una nueva versión de Ekin (v{version}) disponible.\n\n¿Deseas descargarla e instalarla ahora?',
    'main.update.downloading': 'Descargando actualización...',
    'main.update.download_failed': 'Error al descargar el instalador de la actualización. Puedes descargarlo manualmente desde GitHub.',
    'main.onboarding.board_name': 'Mi Primer Tablero',
    'main.onboarding.col_todo': 'Pendientes',
    'main.onboarding.col_doing': 'En Progreso',
    'main.onboarding.col_done': 'Completado',
    'main.onboarding.task_title': 'Explorar Ekin Kanban',
    'main.onboarding.task_description': (
        '¡Bienvenido!\n'
        '\n'
        'Esta es una tarjeta de tarea. Haz click sobre ella para:\n'
        '- Cambiar el título\n'
        '- Añadir una descripción\n'
        '- Configurar etiquetas personalizadas\n'
        '- Registrar tus avances en el Diario personal (a la derecha)'
    ),
    'main.onboarding.tag_category': 'Prioridad',
    'main.onboarding.tag_value': 'Alta',
    'main.onboarding.log_entry': 'He inicializado la aplicación por primera vez. ¡Todo listo para empezar a trabajar!',
    'board_view.column_edit.new_title': 'Nueva Columna',
    'board_view.column_edit.edit_title': 'Editar Columna',
    'board_view.column_edit.name_label': '<b>Nombre de la Columna:</b>',
    'board_view.column_edit.name_placeholder': 'Ej. Pendientes, En Proceso...',
    'board_view.column_edit.color_label': '<b>Color de Acento:</b>',
    'board_view.column_edit.color_dialog_title': 'Seleccionar Color de Columna',
    'board_view.column_edit.save': 'Guardar',
    'board_view.column_edit.cancel': 'Cancelar',
    'board_view.column_edit.warn_title': 'Atención',
    'board_view.column_edit.warn_empty_name': 'El nombre de la columna no puede estar vacío.',
    'board_view.board_selection.target_label': '<b>Selecciona el tablero de destino:</b>',
    'board_view.board_selection.cancel': 'Cancelar',
    'board_view.board_selection.no_other_boards': 'No hay otros tableros',
    'board_view.header.toggle_sidebar_tooltip': 'Mostrar/Ocultar barra lateral',
    'board_view.header.default_title': 'Mi Tablero',
    'board_view.header.counts': '{tasks} tareas · {due} vencen esta semana',
    'board_view.welcome': (
        '💻 ¡Bienvenido a Ekin Kanban!\n'
        '\n'
        'Crea tu primer tablero en el panel lateral\n'
        'para empezar a organizar tus tareas y diarios.'
    ),
    'board_view.add_column_btn': '➕ Nueva Columna',
    'board_view.delete_column.title': 'Eliminar Columna',
    'board_view.delete_column.body': (
        "¿Estás seguro de eliminar la columna '{name}'?\n"
        'Esto borrará todas sus tareas de forma permanente.'
    ),
    'board_view.delete_column.undo_label': 'Eliminar columna',
    'board_view.copy_column.title': 'Copiar Columna',
    'board_view.copy_column.action': 'Copiar',
    'board_view.copy_column.fallback_board_name': 'el tablero seleccionado',
    'board_view.copy_column.done_title': 'Columna Copiada',
    'board_view.copy_column.done_body': "La columna '{column}' y todas sus tareas/logs han sido copiadas con éxito a '{board}'.",
    'board_view.add_task.title': 'Nueva Tarea',
    'board_view.add_task.prompt': 'Introduce el título de la tarea:',
    'board_view.delete_task.undo_label': 'Eliminar tarea',
    'widgets.card.board_link_tooltip': 'Ir al tablero vinculado',
    'widgets.column.collapse_tooltip': 'Plegar columna',
    'widgets.column.expand_tooltip': 'Desplegar columna',
    'widgets.column.edit_tooltip': 'Editar columna (opciones: editar, copiar, eliminar)',
    'widgets.column.title_drag_tooltip': 'Arrastra para reordenar o mover esta columna a otro tablero',
    'widgets.column.task_count_tooltip': '{count} tarea(s)',
    'widgets.column.add_task_btn': '➕ Añadir Tarea',
    'widgets.column.menu_edit': '✏️ Editar Columna',
    'widgets.column.menu_copy': '📋 Copiar a otro tablero...',
    'widgets.column.menu_delete': '🗑️ Eliminar Columna',
    'sidebar.title': 'EKIN',
    'sidebar.boards_subtitle': 'Mis Tableros',
    'sidebar.add_board_btn': '➕ Nuevo Tablero',
    'sidebar.edit_board_btn': '✏️ Editar',
    'sidebar.copy_board_btn': '📋 Copiar',
    'sidebar.delete_board_btn': '🗑️ Borrar',
    'sidebar.archived_btn': '🗄 Archivados',
    'sidebar.archived_tooltip': 'Mostrar/ocultar los tableros archivados (clic derecho en un tablero para archivar)',
    'sidebar.export_btn': '⬇ Exportar...',
    'sidebar.export_tooltip': 'Exportar tableros a JSON, CSV o Markdown',
    'sidebar.import_btn': '⬆ Importar...',
    'sidebar.import_tooltip': 'Importar tableros, columnas y tareas desde un archivo JSON',
    'sidebar.board_config_tooltip': 'Opciones del tablero',
    'sidebar.board_config.title': 'Opciones del tablero',
    'sidebar.bell_tooltip': 'Tareas atrasadas o que vencen hoy o mañana',
    'sidebar.search_tooltip': 'Buscar tareas (Ctrl+F)',
    'sidebar.calendar_tooltip': 'Abrir vista de calendario',
    'sidebar.settings_tooltip': 'Ajustes (tema, notificaciones)',
    'sidebar.shortcuts_tooltip': 'Atajos de teclado (Ctrl+/)',
    'sidebar.notifications.header': '🔔  Vencimientos',
    'sidebar.notifications.empty': 'No hay tareas atrasadas ni próximas. ✅',
    'sidebar.notifications.group_overdue': 'ATRASADAS',
    'sidebar.notifications.group_today': 'HOY',
    'sidebar.notifications.group_tomorrow': 'MAÑANA',
    'sidebar.notifications.item_no_title': '(sin título)',
    'sidebar.notifications.item_tooltip': '{board} · vence {due_date}',
    'sidebar.board_button.archived_tooltip': 'Tablero archivado — clic derecho para desarchivar',
    'sidebar.board_button.menu_unarchive': '📤 Desarchivar tablero',
    'sidebar.board_button.menu_archive': '🗄 Archivar tablero',
    'sidebar.board_edit.new_title': 'Nuevo Tablero',
    'sidebar.board_edit.edit_title': 'Editar Tablero',
    'sidebar.board_edit.copy_title': 'Copiar Tablero',
    'sidebar.board_edit.copy_default_name': '{name} - Copia',
    'sidebar.board_edit.name_label': '<b>Nombre del Tablero:</b>',
    'sidebar.board_edit.name_placeholder': 'Ej. Trabajo, Personal, Viaje...',
    'sidebar.board_edit.color_label': '<b>Color de Fondo:</b>',
    'sidebar.board_edit.color_dialog_title': 'Seleccionar Color del Tablero',
    'sidebar.board_edit.save': 'Guardar',
    'sidebar.board_edit.cancel': 'Cancelar',
    'sidebar.board_edit.warn_title': 'Atención',
    'sidebar.board_edit.warn_empty_name': 'El nombre del tablero no puede estar vacío.',
    'sidebar.export_menu.json': 'JSON (.json)',
    'sidebar.export_menu.csv': 'CSV de tareas (.csv)',
    'sidebar.export_menu.markdown': 'Informe Markdown (.md)',
    'sidebar.export.dialog_title': 'Exportar {label}',
    'sidebar.export.error_title': 'Error al exportar',
    'sidebar.export.error_body': (
        'No se pudo exportar:\n'
        '{error}'
    ),
    'sidebar.export.done_title': 'Exportado',
    'sidebar.export.done_body': (
        'Exportación {label} guardada en:\n'
        '{path}'
    ),
    'sidebar.delete_board.title': 'Eliminar Tablero',
    'sidebar.delete_board.body': (
        "¿Estás seguro de eliminar el tablero '{name}'?\n"
        'Esto borrará todas sus columnas, tareas y diarios asociados de forma permanente.'
    ),
    'sidebar.delete_board.undo_label': 'Eliminar tablero',
    'export_dialog.window_title': 'Exportar Tableros',
    'export_dialog.scope_group': '<b>Alcance de la exportación:</b>',
    'export_dialog.scope_all': 'Todos los tableros (incluidos archivados)',
    'export_dialog.scope_current': 'Solo el tablero activo: «{name}»',
    'export_dialog.format_group': '<b>Formato de archivo:</b>',
    'export_dialog.format_json': 'JSON (.json) — Datos completos o plantillas',
    'export_dialog.json_include_tasks': 'Incluir tareas, etiquetas, enlaces y diario',
    'export_dialog.json_template_hint': 'Si se desmarca, se exportará únicamente la estructura de columnas como plantilla reusable.',
    'export_dialog.format_csv': 'CSV (.csv) — Lista de tareas para hojas de cálculo (Excel / Sheets)',
    'export_dialog.format_markdown': 'Markdown (.md) — Informe legible del proyecto',
    'export_dialog.md_include_details': 'Incluir descripciones, enlaces y diario en el informe',
    'export_dialog.export_btn': '💾 Exportar a Archivo...',
    'export_dialog.cancel_btn': 'Cancelar',
    'export_dialog.save_title': 'Guardar archivo de exportación',
    'export_dialog.done_title': 'Exportación Completada',
    'export_dialog.done_body': (
        'Exportación {label} guardada correctamente en:\n'
        '{path}'
    ),
    'export_dialog.error_title': 'Error en la exportación',
    'export_dialog.error_body': (
        'No se pudo completar la exportación:\n'
        '{error}'
    ),
    'import_dialog.window_title': 'Importar Tableros desde JSON',
    'import_dialog.open_title': 'Seleccionar archivo JSON para importar',
    'import_dialog.file_label': '<b>Archivo:</b> {filename}',
    'import_dialog.summary_label': 'Se han detectado <b>{boards}</b> tablero(s), <b>{columns}</b> columna(s) y <b>{tasks}</b> tarea(s).',
    'import_dialog.options_group': '<b>Opciones de importación:</b>',
    'import_dialog.opt_full': 'Importar todo (tableros, columnas, tareas, etiquetas, enlaces y diario)',
    'import_dialog.opt_structure_only': 'Importar solo estructura de columnas (como plantilla sin tareas)',
    'import_dialog.template_only_hint': 'Este archivo contiene únicamente estructura de columnas (plantilla).',
    'import_dialog.import_btn': '📥 Importar a Ekin',
    'import_dialog.cancel_btn': 'Cancelar',
    'import_dialog.done_title': 'Importación Completada',
    'import_dialog.done_body': 'Se han importado {count} tablero(s) con éxito.',
    'import_dialog.error_title': 'Error en la importación',
    'import_dialog.error_body': (
        'No se pudo importar el archivo:\n'
        '{error}'
    ),
    'calendar.chip_no_title': '(sin título)',
    'calendar.chip_tooltip': (
        '{board} · {title}\n'
        'Arrastra a otro día para reprogramar'
    ),
    'calendar.more_tasks': '+{count} más',
    'calendar.today_btn': 'Hoy',
    'calendar.mode_month': 'Mes',
    'calendar.mode_week': 'Semana',
    'calendar.mode_day': 'Día',
    'calendar.mode_tooltip': 'Vista del calendario',
    'calendar.board_filter_tooltip': 'Filtrar por tablero',
    'calendar.settings_btn': 'Ajustes',
    'calendar.settings_tooltip': 'Sincronizar / exportar a Google, Apple u Outlook',
    'calendar.close_btn': 'Cerrar',
    'calendar.close_tooltip': 'Volver a la vista de tablero',
    'calendar.all_boards': 'Todos los tableros',
    'calendar.week_period': 'Semana {start} – {end}',
    'calendar.error_title': 'Error',
    'calendar.settings_dialog.title': 'Ajustes de Calendario',
    'calendar.settings_dialog.header': '<b>Sincronización de calendario</b>',
    'calendar.settings_dialog.info': 'Ekin exporta tus tareas con fecha de vencimiento a un archivo estándar <b>iCalendar (.ics)</b>, compatible con Google Calendar, Apple Calendar y Outlook.',
    'calendar.settings_dialog.sync_title': '<b>Sincronización automática</b> (recomendado)',
    'calendar.settings_dialog.sync_desc': 'Ekin mantiene un archivo .ics <b>siempre al día</b> (lo reescribe al cambiar tareas). Guárdalo en una carpeta de Dropbox / OneDrive / Google Drive y <b>suscríbete</b> a él una sola vez: a partir de ahí se actualiza solo.',
    'calendar.settings_dialog.sync_board_tooltip': 'Sincronizar automáticamente todos los tableros o solo uno',
    'calendar.settings_dialog.configure_btn_initial': 'Elegir archivo…',
    'calendar.settings_dialog.configure_btn_change': 'Cambiar archivo…',
    'calendar.settings_dialog.disable_btn': 'Desactivar',
    'calendar.settings_dialog.subscribe_title': '<b>Suscribirse en tu calendario</b>',
    'calendar.settings_dialog.subscribe_desc': 'Sube el archivo .ics a una carpeta pública (Google Drive / Dropbox / OneDrive) y pega aquí su <b>URL pública</b>. Ekin la guarda y, según el botón, la copia al portapapeles y abre la página del proveedor para <b>añadir un calendario por URL</b> (el paso manual que suele fallar). Guía detallada abajo.',
    'calendar.settings_dialog.public_url_placeholder': 'https://…/ekin_calendario.ics',
    'calendar.settings_dialog.google_btn_tooltip': 'Copiar la URL y abrir «Añadir por URL» de Google Calendar',
    'calendar.settings_dialog.outlook_btn_tooltip': 'Copiar la URL y abrir «Suscribirse desde la web» de Outlook',
    'calendar.settings_dialog.apple_btn_tooltip': 'Copiar la URL como enlace webcal:// para iPhone/Mac',
    'calendar.export_once_btn': 'Exportar copia…',
    'calendar.export_once_tooltip': 'Guardar una copia .ics puntual (snapshot) en otra ubicación',
    'calendar.export_board_tooltip': 'Exportar el calendario de todos los tableros o de uno solo',
    'calendar.settings_dialog.close_btn': 'Cerrar',
    'calendar.settings_dialog.sync_active': 'Sincronizando en:<br><code>{path}</code>',
    'calendar.settings_dialog.sync_inactive': 'Sincronización automática desactivada.',
    'calendar.settings_dialog.configure_file_dialog_title': 'Archivo de sincronización',
    'calendar.settings_dialog.configure_error_body': (
        'No se pudo crear el archivo:\n'
        '{error}'
    ),
    'calendar.settings_dialog.sync_activated_title': 'Sincronización activada',
    'calendar.settings_dialog.sync_activated_body': (
        'Ekin mantendrá {count} tarea(s) sincronizadas en:\n'
        '{path}\n'
        '\n'
        'Suscríbete a este archivo una vez desde tu calendario y se actualizará solo.'
    ),
    'calendar.settings_dialog.empty_url_title': 'URL vacía',
    'calendar.settings_dialog.empty_url_body': 'Pega primero la URL pública de tu archivo .ics (el enlace compartido de la carpeta en la nube donde lo sincronizas).',
    'calendar.settings_dialog.google_title': 'Google Calendar',
    'calendar.settings_dialog.google_body': (
        'He copiado la URL al portapapeles y abierto Google Calendar (en el ordenador; la app de móvil no permite añadir por URL).\n'
        '\n'
        '1. Menú lateral izquierdo → «Otros calendarios» → «+» → «Desde una URL».\n'
        '2. Pega la URL (Ctrl+V) y pulsa «Añadir calendario».\n'
        '\n'
        'Nota: Google recarga los calendarios por URL de forma lenta (cada varias horas, hasta ~24 h) y no se puede forzar.'
    ),
    'calendar.settings_dialog.outlook_title': 'Outlook Calendar',
    'calendar.settings_dialog.outlook_body': (
        'He copiado la URL al portapapeles y abierto Outlook en el navegador.\n'
        '\n'
        '1. En Outlook.com: «Agregar calendario» → «Suscribirse desde la web».\n'
        '   (En Outlook de trabajo/Microsoft 365 la ruta es outlook.office.com → misma opción.)\n'
        '2. Pega la URL (Ctrl+V), ponle un nombre y color, y pulsa «Importar»/«Suscribirse».\n'
        '\n'
        'El Outlook de escritorio (clásico) también admite: Inicio → «Abrir calendario» → «De Internet…» y pegar la URL.'
    ),
    'calendar.settings_dialog.apple_title': 'Apple / iCloud',
    'calendar.settings_dialog.apple_body': (
        'He copiado la URL como enlace <b>webcal://</b> al portapapeles (así iOS/macOS la reconocen como suscripción). Pégala aquí:\n'
        '\n'
        '• iPhone/iPad: Ajustes → Calendario → Cuentas → Añadir cuenta → Otra → «Añadir calendario suscrito» → pega el enlace → Siguiente.\n'
        '• Mac (app Calendario): Archivo → «Nueva suscripción de calendario…» → pega el enlace → Suscribirse; ahí puedes fijar la frecuencia de actualización (incluso cada pocos minutos).\n'
        '\n'
        'La suscripción se guarda en iCloud y se ve en todos tus dispositivos Apple.'
    ),
    'calendar.settings_dialog.provider_guide': '<b>📋 Cómo suscribirte (se mantiene sincronizado, sin duplicados)</b><p><b>0) Consigue una URL pública y directa del .ics.</b> Guarda el archivo en una carpeta de la nube y comparte el enlace <i>directo al archivo</i> (no a una página de vista previa):<ul><li><b>Google Drive</b>: compartir «Cualquiera con el enlace». El enlace normal apunta a una vista HTML; usa la forma de descarga directa <code>https://drive.google.com/uc?export=download&id=ID_DEL_ARCHIVO</code>.</li><li><b>Dropbox</b>: copia el enlace y cambia el final <code>?dl=0</code> por <code>?dl=1</code>.</li><li><b>OneDrive</b>: «Compartir» → «Cualquier persona con el vínculo» → copia el enlace.</li></ul>Ábrela en una ventana de incógnito: debes ver texto que empieza por <code>BEGIN:VCALENDAR</code>. Si ves un login o una vista previa, el enlace no sirve.</p><p><b>🟦 Google Calendar</b> (solo en el ordenador): menú lateral → «Otros calendarios» → «+» → «Desde una URL» → pega la URL → «Añadir calendario». Refresco lento (varias horas).</p><p><b>🟧 Outlook</b>: en <i>Outlook.com/365 (web)</i> → «Agregar calendario» → «Suscribirse desde la web» → pega la URL → nombre/color → «Importar». En <i>Outlook de escritorio</i> → Inicio → «Abrir calendario» → «De Internet…» → pega la URL.</p><p><b>🍎 Apple / iCloud</b> (usa un enlace <code>webcal://</code>): <i>iPhone/iPad</i> → Ajustes → Calendario → Cuentas → Añadir cuenta → Otra → «Añadir calendario suscrito» → pega el enlace. <i>Mac</i> → app Calendario → Archivo → «Nueva suscripción de calendario…» → pega el enlace (puedes elegir cada cuánto se actualiza).</p><p><b>⚠️ Suscribir ≠ Importar.</b> «Importar» una copia es una foto fija: no refleja cambios ni borrados y puede duplicar eventos. Suscríbete a la URL para que se actualice solo.</p>',
    'calendar.export_dialog_title': 'Exportar copia del calendario',
    'calendar.export_error_body': (
        'No se pudo exportar el calendario:\n'
        '{error}'
    ),
    'calendar.export_done_title': 'Exportado',
    'calendar.export_done_body': (
        'Se exportaron {count} tarea(s) con fecha a:\n'
        '{path}\n'
        '\n'
        'Recuerda: una copia importada es una foto fija; para que se mantenga al día, usa la sincronización automática de arriba y suscríbete al archivo.'
    ),
    'search.window_title': 'Buscar tareas',
    'search.header': '<b>Buscar tareas</b>',
    'search.text_placeholder': 'Título o descripción…',
    'search.all_boards': 'Todos los tableros',
    'search.all_tags': 'Todas las etiquetas',
    'search.only_due_checkbox': 'Solo con vencimiento',
    'search.close_btn': 'Cerrar',
    'search.result_count': '{count} resultado(s)',
    'search.no_results': 'Sin resultados.',
    'search.result_no_title': '(sin título)',
    'search.result_tooltip': '{board} · {column}',
    'settings.window_title': 'Ajustes',
    'settings.header': 'Ajustes',
    'settings.theme_label': 'Tema:',
    'settings.theme_dark': 'Oscuro',
    'settings.theme_light': 'Claro',
    'settings.theme_desc': 'Se aplica al instante — sin reiniciar.',
    'settings.notifications_label': 'Notificaciones de Windows para tareas que vencen hoy',
    'settings.notifications_checkbox': 'Mostrar avisos de Windows para tareas que vencen hoy',
    'settings.notifications_desc': 'Un resumen al abrir Ekin, luego una vez al día.',
    'settings.timer_alert_label': 'Avisar en la tarjeta si un temporizador lleva más de:',
    'settings.timer_alert_suffix': ' h',
    'settings.timer_alert_desc': 'Las tareas inactivas se tornan terracota en el tablero.',
    'settings.geometry_hint': 'El tamaño y la posición de la ventana se recuerdan automáticamente.',
    'settings.close_btn': 'Cerrar',
    'shortcuts.window_title': 'Atajos de teclado',
    'shortcuts.header': '<b>Atajos de teclado</b>',
    'shortcuts.section_general': 'General y navegación',
    'shortcuts.section_editor': 'Editor de texto enriquecido (descripción y diario)',
    'shortcuts.item_search': 'Ctrl+F — Búsqueda global de tareas',
    'shortcuts.item_new_task': 'Ctrl+N — Nueva tarea en la última columna con la que interactuaste (si no hay ninguna, la primera del tablero activo); dentro del editor de texto, Ctrl+N es Negrita',
    'shortcuts.item_new_column': 'Ctrl+Shift+N — Nueva columna en el tablero activo',
    'shortcuts.item_prev_next_board': 'Alt+↑ / Alt+↓ — Tablero anterior / siguiente',
    'shortcuts.item_jump_board': 'Ctrl+1 … Ctrl+9 — Saltar directamente al tablero Nº de la barra lateral',
    'shortcuts.item_calendar': 'Ctrl+Shift+C — Abrir el Calendario',
    'shortcuts.item_settings': 'Ctrl+, — Abrir Ajustes',
    'shortcuts.item_shortcuts': 'Ctrl+/ — Mostrar esta ventana',
    'shortcuts.item_undo_redo': 'Ctrl+Z / Ctrl+Y (o Ctrl+Shift+Z) — Deshacer / Rehacer',
    'shortcuts.item_close_dialog': 'Esc — Cerrar el diálogo abierto',
    'shortcuts.item_bold': 'Ctrl+B o Ctrl+N — Negrita (dentro del editor)',
    'shortcuts.item_italic': 'Ctrl+K o Ctrl+I — Cursiva (dentro del editor)',
    'shortcuts.item_strike': 'Ctrl+Shift+X — Tachado (dentro del editor)',
    'shortcuts.item_align': 'Ctrl+L / Ctrl+E / Ctrl+R / Ctrl+J — Alinear texto (izq, centro, der, justificado)',
    'shortcuts.item_case': 'Ctrl+Shift+U / Ctrl+Shift+L / Shift+F3 — Cambiar a MAYÚSCULAS / minúsculas',
    'shortcuts.item_nest_bullet': 'Tab (sobre una viñeta) — Anidar la viñeta (dentro del editor)',
    'shortcuts.item_quote': "Ctrl+Shift+Q o escribir '> ' · Bloque de cita / llamada (dentro del editor)",
    'shortcuts.item_paste_plain': 'Ctrl+Shift+V · Pegar como texto plano (dentro del editor)',
    'shortcuts.item_arrow': 'Escribir «-->» se convierte en → automáticamente (dentro del editor)',
    'shortcuts.item_add_log': 'Ctrl+Enter — Añadir la nota al Diario (detalle de tarea)',
    'shortcuts.hint': 'Pulsa Ctrl+/ en cualquier momento para volver a ver esta ventana.',
    'shortcuts.close_btn': 'Cerrar',
    'markdown_edit.bold_tooltip': 'Negrita (Ctrl+B o Ctrl+N)',
    'markdown_edit.italic_tooltip': 'Cursiva (Ctrl+K o Ctrl+I)',
    'markdown_edit.strike_tooltip': 'Tachado (Ctrl+Shift+X)',
    'markdown_edit.align_left_tooltip': 'Alinear a la izquierda (Ctrl+L)',
    'markdown_edit.align_center_tooltip': 'Centrar texto (Ctrl+E)',
    'markdown_edit.align_right_tooltip': 'Alinear a la derecha (Ctrl+R)',
    'markdown_edit.align_justify_tooltip': 'Justificar texto (Ctrl+J)',
    'markdown_edit.upper_tooltip': 'Convertir a MAYÚSCULAS (Ctrl+Shift+U)',
    'markdown_edit.lower_tooltip': 'Convertir a minúsculas (Ctrl+Shift+L)',
    'markdown_edit.context_upper': 'Convertir a MAYÚSCULAS',
    'markdown_edit.context_lower': 'Convertir a minúsculas',
    'markdown_edit.bullet_tooltip': 'Lista con viñetas  ·  también con «* », «- » o «+ »',
    'markdown_edit.hr_tooltip': 'Línea separadora  ·  también escribiendo «---»',
    'markdown_edit.arrow_tooltip': 'Insertar flecha (→)  ·  también escribiendo «-->»',
    'markdown_edit.color_tooltip': 'Color del texto',
    'markdown_edit.color_default': 'Color por defecto',
    'markdown_edit.color_more': 'Más colores…',
    'markdown_edit.color_dialog_title': 'Seleccionar color de texto',
    'markdown_edit.table_tooltip': 'Insertar tabla',
    'markdown_edit.table_dialog_title': 'Insertar tabla',
    'markdown_edit.table_rows_label': 'Filas:',
    'markdown_edit.table_cols_label': 'Columnas:',
    'markdown_edit.code_tooltip': 'Insertar bloque de código  ·  también con «```»',
    'markdown_edit.code_dialog_title': 'Insertar bloque de código',
    'markdown_edit.code_lang_label': 'Lenguaje de programación:',
    'markdown_edit.code_text_label': 'Código:',
    'markdown_edit.code_insert_btn': 'Insertar',
    'markdown_edit.code_cancel_btn': 'Cancelar',
    'markdown_edit.quote_tooltip': "Bloque de cita / llamada (Ctrl+Shift+Q, o escribe '> ' al inicio)",
    'markdown_edit.quote_placeholder': 'Escribe una cita...',
    'markdown_edit.paste_plain_menu': 'Pegar texto plano (Ctrl+Shift+V)',
    'markdown_edit.paste_formatted_menu': 'Pegar con formato',
    'markdown_edit.image_size_menu': 'Tamaño de imagen',
    'markdown_edit.image_size_25': '25% ancho',
    'markdown_edit.image_size_50': '50% ancho',
    'markdown_edit.image_size_75': '75% ancho',
    'markdown_edit.image_size_100': '100% ancho (ajustar al editor)',
    'markdown_edit.image_size_custom': 'Ancho personalizado (px)…',
    'markdown_edit.image_size_dialog_title': 'Redimensionar imagen',
    'markdown_edit.image_size_dialog_label': 'Ancho de imagen en píxeles:',
    'markdown_edit.delete_code_btn': 'Borrar',
    'markdown_edit.delete_code_tooltip': 'Eliminar este bloque de código',
    'markdown_edit.delete_code_btn_menu': 'Eliminar bloque de código',
    'markdown_edit.link_tooltip': 'Insertar enlace web (URL)',
    'markdown_edit.link_dialog_title': 'Insertar enlace',
    'markdown_edit.link_url_label': 'Dirección web (URL):',
    'markdown_edit.link_text_label': 'Texto a mostrar (opcional):',
    'markdown_edit.link_insert_btn': 'Insertar',
    'markdown_edit.link_cancel_btn': 'Cancelar',
    'log_entry.edit_tooltip': 'Editar comentario',
    'log_entry.delete_tooltip': 'Eliminar comentario',
    'log_entry.save_btn': 'Guardar',
    'log_entry.cancel_btn': 'Cancelar',
    'image_preview.window_title': 'Vista previa de imagen',
    'tag_manager.window_title': 'Gestionar Etiquetas',
    'tag_manager.header': '<b>Etiquetas</b>',
    'tag_manager.add_category_btn': 'Nueva',
    'tag_manager.category_action_label': 'Renombrar etiqueta',
    'tag_manager.delete_category_tooltip': 'Eliminar etiqueta',
    'tag_manager.values_title_default': '<b>Valores</b>',
    'tag_manager.values_title_for_category': '<b>Valores de «{category}»</b>',
    'tag_manager.new_value_placeholder': 'Nuevo valor (ej. Alta)…',
    'tag_manager.new_value_color_tooltip': 'Color del nuevo valor',
    'tag_manager.add_value_btn': 'Añadir valor',
    'tag_manager.close_btn': 'Cerrar',
    'tag_manager.add_category_dialog_title': 'Nueva etiqueta',
    'tag_manager.add_category_prompt': 'Nombre de la etiqueta (ej. Prioridad):',
    'tag_manager.new_name_prompt': 'Nuevo nombre:',
    'tag_manager.delete_category_body': (
        '¿Eliminar la etiqueta «{category}» y todos sus valores?\n'
        'Se quitará de todas las tareas que la usen.'
    ),
    'tag_manager.no_category_hint': 'Crea o selecciona una etiqueta a la izquierda para definir sus valores.',
    'tag_manager.no_values_hint': 'Aún no hay valores. Añade el primero abajo.',
    'tag_manager.swatch_tooltip': 'Cambiar color',
    'tag_manager.rename_value_tooltip': 'Renombrar valor',
    'tag_manager.delete_value_tooltip': 'Eliminar valor',
    'tag_manager.color_dialog_title': 'Color del valor',
    'tag_manager.warn_title': 'Atención',
    'tag_manager.duplicate_value_body': 'Ya existe un valor con ese nombre en esta etiqueta.',
    'tag_manager.delete_value_body': (
        '¿Eliminar el valor «{value}»?\n'
        'Se quitará de las tareas que lo tengan asignado.'
    ),
    'tag_picker.title_edit': 'Editar Etiqueta',
    'tag_picker.title_assign': 'Asignar Etiqueta',
    'tag_picker.category_label': '<b>Etiqueta</b>',
    'tag_picker.value_label': '<b>Valor</b>',
    'tag_picker.manage_btn': 'Gestionar etiquetas…',
    'tag_picker.accept_btn': 'Aceptar',
    'tag_picker.cancel_btn': 'Cancelar',
    'tag_picker.none_option': '— Ninguno (ocultar) —',
    'tag_picker.no_categories_hint': 'No hay etiquetas definidas. Usa «Gestionar etiquetas…» para crear una.',
    'tag_picker.no_values_hint': 'Esta etiqueta no tiene valores. Añádelos en «Gestionar etiquetas…».',
    'tag_picker.warn_title': 'Atención',
    'tag_picker.warn_no_category': 'Primero crea una etiqueta en «Gestionar etiquetas…».',
    'tag_picker.warn_no_value': 'Selecciona un valor (o créalo en «Gestionar etiquetas…»).',
    'task_detail.window_title': 'Detalles de la Tarea',
    'task_detail.title_label': '<b>Título de la Tarea</b>',
    'task_detail.title_placeholder': 'Ej. Escribir informe mensual...',
    'task_detail.description_label': '<b>Descripción / Notas</b>',
    'task_detail.description_placeholder': 'Añade detalles sobre esta tarea...',
    'task_detail.timer_label': '<b>Temporizador:</b>',
    'task_detail.timer_start_btn': '▶ Iniciar',
    'task_detail.timer_restart_btn': '↺ Reiniciar',
    'task_detail.timer_clear_btn': 'Detener',
    'task_detail.timer_clear_tooltip': 'Detiene el temporizador y quita la insignia de la tarjeta',
    'task_detail.timer_elapsed': 'En marcha desde hace {elapsed}',
    'task_detail.due_label': '<b>Vencimiento:</b>',
    'task_detail.due_enable_checkbox': 'Habilitar',
    'task_detail.due_time_checkbox': 'Hora',
    'task_detail.due_time_tooltip': 'Añadir hora al vencimiento (crea un aviso en el calendario)',
    'task_detail.recurrence_none': 'Sin repetir',
    'task_detail.recurrence_daily': 'Diaria',
    'task_detail.recurrence_weekly': 'Semanal',
    'task_detail.recurrence_monthly': 'Mensual',
    'task_detail.recurrence_tooltip': 'Repetir la tarea: al pasar la fecha, se adelanta sola',
    'task_detail.tags_label': '<b>Etiquetas:</b>',
    'task_detail.assign_tag_btn': 'Asignar Etiqueta',
    'task_detail.manage_tags_btn': 'Gestionar',
    'task_detail.manage_tags_tooltip': 'Definir etiquetas permanentes y sus valores',
    'task_detail.priority_label': '<b>Prioridad:</b>',
    'task_detail.priority_tooltip': 'Prioridad rápida de la tarea (aparece como etiqueta en el tablero)',
    'task_detail.priority_category_name': 'Prioridad',
    'task_detail.priority_none': '— Sin prioridad —',
    'task_detail.priority_low': 'Baja',
    'task_detail.priority_medium': 'Media',
    'task_detail.priority_high': 'Alta',
    'task_detail.linked_board_label': '<b>Tablero vinculado:</b>',
    'task_detail.linked_board_tooltip': 'Enlaza esta tarea con otro tablero (aparece como pastilla clicable en la tarjeta)',
    'task_detail.linked_board_none': '— Sin vincular —',
    'task_detail.links_label': '<b>Enlaces / adjuntos:</b>',
    'task_detail.link_url_placeholder': 'URL o ruta…',
    'task_detail.link_label_placeholder': 'Nombre (opcional)',
    'task_detail.add_link_tooltip': 'Añadir enlace',
    'task_detail.browse_file_tooltip': 'Buscar un archivo local del PC para adjuntar',
    'task_detail.browse_file_title': 'Seleccionar archivo para adjuntar',
    'task_detail.link_missing_tooltip': 'Archivo no encontrado: {path}',
    'task_detail.link_open_failed_title': 'No se pudo abrir',
    'task_detail.link_open_failed_msg': 'No se pudo abrir el enlace o el archivo adjunto. Puede que se haya movido o eliminado.',
    'task_detail.link_security_title': 'Aviso de seguridad',
    'task_detail.link_security_executable_msg': (
        "'{target}' es un programa o script ejecutable ({ext}).\n"
        '\n'
        'Abrir archivos ejecutables desde tableros compartidos o que no sean de confianza puede dañar tu ordenador.\n'
        '\n'
        '¿Seguro que deseas abrirlo?'
    ),
    'task_detail.link_security_unc_msg': (
        "'{target}' es una ruta de recurso compartido de red (UNC).\n"
        '\n'
        'Abrir rutas de red desde tableros compartidos o que no sean de confianza puede exponer tus credenciales de red o acceder a archivos remotos.\n'
        '\n'
        '¿Seguro que deseas abrirlo?'
    ),
    'task_detail.link_security_unc_executable_msg': (
        "'{target}' es un programa o script ejecutable en un recurso compartido de red remoto ({ext}).\n"
        '\n'
        'Abrir ejecutables remotos desde tableros compartidos o que no sean de confianza puede dañar tu ordenador.\n'
        '\n'
        '¿Seguro que deseas abrirlo?'
    ),
    'task_detail.link_security_scheme_msg': (
        "'{target}' usa un protocolo no reconocido o potencialmente inseguro ({scheme}).\n"
        '\n'
        'Abrir este enlace puede dañar tu ordenador.\n'
        '\n'
        '¿Seguro que deseas abrirlo?'
    ),
    'task_detail.delete_task_btn': 'Eliminar',
    'task_detail.save_btn': 'Guardar Cambios',
    'task_detail.close_btn': 'Cerrar',
    'task_detail.log_header': 'Diario',
    'task_detail.entries_count': '{count} entradas',
    'task_detail.notes_kicker': 'NOTAS',
    'task_detail.notes_last_edited': 'Última edición: {timestamp}',
    'task_detail.saves_hint': 'Los cambios se guardan al escribir',
    'task_detail.kicker': '{board} · {column}',
    'task_detail.log_input_placeholder': 'Escribe una nota o actualización en el diario... (Ctrl+Enter para guardar)',
    'task_detail.add_log_btn': 'Añadir al Diario',
    'task_detail.load_error_title': 'Error',
    'task_detail.load_error_body': 'No se pudo cargar la tarea.',
    'task_detail.no_tags_hint': 'Sin etiquetas. Pulsa «Asignar Etiqueta».',
    'task_detail.tag_pill_tooltip': 'Clic para cambiar el valor',
    'task_detail.tag_pill_remove_tooltip': 'Quitar de la tarea',
    'task_detail.warn_title': 'Atención',
    'task_detail.warn_empty_title': 'El título de la tarea no puede estar vacío.',
    'task_detail.delete_task_title': 'Confirmar Eliminación',
    'task_detail.delete_task_body': '¿Estás seguro de que deseas eliminar esta tarea de forma permanente? No se podrá recuperar.',
    'task_detail.no_links_hint': 'Sin enlaces.',
    'task_detail.delete_link_tooltip': 'Eliminar enlace',
    'task_detail.delete_log_title': 'Eliminar Entrada',
    'task_detail.delete_log_body': '¿Estás seguro de que deseas borrar esta entrada del diario?',
    'board_view.bulk_add_btn': 'Añadir tareas en masa',
    'board_view.bulk_add_tooltip': 'Añadir múltiples tareas a la vez mediante una tabla',
    'bulk_add.dialog_title': 'Añadir tareas en masa',
    'bulk_add.header': '<b>Añadir tareas en masa</b>',
    'bulk_add.instructions': 'Define múltiples tareas en la tabla inferior. También puedes pegar filas copiadas desde Excel o Sheets.',
    'bulk_add.col_title': 'Título *',
    'bulk_add.col_description': 'Descripción',
    'bulk_add.col_column': 'Columna',
    'bulk_add.add_row_btn': 'Añadir fila',
    'bulk_add.del_row_btn': 'Eliminar fila',
    'bulk_add.create_btn': 'Crear tareas',
    'bulk_add.cancel_btn': 'Cancelar',
    'bulk_add.warn_no_tasks': 'Introduce al menos una tarea con título.',
    'bulk_add.success_toast': '{count} tarea(s) creadas con éxito.',
    'sync.menu_open_shared': 'Conectar archivo .ekboard existente…',
    'sync.or_connect_existing_prompt': '… o conecta un tablero cloud compartido …',
    'sync.open_shared_title': 'Seleccionar archivo .ekboard existente de Cloud / red',
    'sync.open_shared_success': "Tablero compartido '{name}' conectado correctamente.",
    'sync.open_shared_exists': 'Este tablero ya está en tu lista de tableros.',
    'sync.link_btn': 'Vincular con Cloud',
    'sync.link_tooltip': 'Vincular este tablero a Google Drive, Dropbox, OneDrive o carpeta compartida (.ekboard)',
    'sync.info_dialog_title': 'Vincular Tablero con Cloud',
    'sync.info_header': 'Sincronización en la Nube con Ekin',
    'sync.info_subtitle': 'Colabora en tiempo real con Google Drive, Dropbox, OneDrive o carpetas en red local.',
    'sync.info_desc': 'Ekin sincroniza este tablero generando un único archivo compartido (.ekboard). Cualquier cambio realizado por ti o tu equipo se detecta y fusiona automáticamente en segundo plano mediante un motor reactivo sin pérdida de información (No-Data-Loss).',
    'sync.info_providers_title': 'Instrucciones por proveedor de nube:',
    'sync.info_gdrive': '<b>🟦 Google Drive</b>: Guarda el archivo dentro de tu unidad o carpeta de Google Drive sincronizada en este PC (ej. <i>G:\\Mi unidad\\...</i> o <i>C:\\Usuarios\\...\\Google Drive</i>).',
    'sync.info_dropbox': '<b>📦 Dropbox</b>: Guarda el archivo en tu carpeta de Dropbox sincronizada (ej. <i>C:\\Usuarios\\...\\Dropbox</i>).',
    'sync.info_onedrive': '<b>☁️ OneDrive</b>: Guarda el archivo en tu carpeta de OneDrive (ej. <i>C:\\Usuarios\\...\\OneDrive</i>).',
    'sync.info_other': '<b>🌐 Otras Nubes o Red Local</b>: También es compatible con Nextcloud, Syncthing o cualquier carpeta compartida de red local (SMB).',
    'sync.info_continue_btn': 'Continuar y Seleccionar Carpeta…',
    'sync.info_cancel_btn': 'Cancelar',
    'sync.synced_badge': 'Sincronizado',
    'sync.syncing': 'Sincronizando…',
    'sync.offline_badge': 'Tablero local (sin sincronizar)',
    'sync.menu_sync_now': 'Sincronizar ahora',
    'sync.menu_open_location': 'Abrir ubicación del archivo…',
    'sync.menu_unlink': 'Desvincular sincronización',
    'sync.dialog_title_link': 'Seleccionar o crear archivo compartido de tablero',
    'sync.dialog_filter': 'Tablero Ekin (*.ekboard);;Todos los archivos (*.*)',
    'sync.unlink_confirm_title': 'Desvincular Sincronización',
    'sync.unlink_confirm_body': '¿Deseas desvincular este tablero del archivo compartido? El tablero seguirá funcionando localmente sin afectar a otros usuarios.',
    'sync.success_title': 'Sincronización Exitosa',
    'sync.error_title': 'Error de Sincronización',
    'sync.conflict_merged_toast': 'Se han fusionado cambios concurrentes sin pérdida de datos.',
    'ai_spec.selection_count': '✨ {count} tarea(s) seleccionada(s)',
    'ai_spec.generate_spec_btn': 'Generar SPEC con IA Local',
    'ai_spec.clear_selection_btn': 'Deseleccionar',
    'ai_spec.dialog_title': 'Generador de SPEC para Agentes de IA',
    'ai_spec.mode_label': 'Modo de Especificación:',
    'ai_spec.model_label': 'Modelo (Ollama):',
    'ai_spec.refresh_models_tooltip': 'Escanear modelos de Ollama activos (localhost:11434)',
    'ai_spec.mode_coding_agent': 'Arquitectura y Plan de Código (Antigravity / Claude Code / Cursor)',
    'ai_spec.mode_user_stories': 'Historias de Usuario & Criterios de Aceptación (Gherkin)',
    'ai_spec.mode_qa_plan': 'Plan de Pruebas & Matriz de QA',
    'ai_spec.generate_btn': 'Generar SPEC',
    'ai_spec.copy_btn': 'Copiar SPEC',
    'ai_spec.save_btn': 'Guardar Archivo…',
    'ai_spec.create_task_btn': 'Crear como Tarea en el Tablero',
    'ai_spec.model_status_label': 'Motor de IA:',
    'ai_spec.status_ready': 'Listo para generar',
    'ai_spec.status_generating': 'Generando especificación con IA local…',
    'ai_spec.copied_toast': '¡SPEC copiada al portapapeles!',
    'ai_spec.saved_toast': 'Especificación guardada correctamente.',
    'ai_spec.task_created_toast': 'Tarea creada en el tablero con la especificación.',
    'ai_spec.download_model_title': 'Descargar Modelo de IA Local Autónomo',
    'ai_spec.download_model_prompt': (
        'Ekin puede ejecutar un modelo de IA local autónomo (Qwen 2.5 Coder 1.5B, ~980 MB) sin requerir software adicional ni enviar tus datos a la nube.\n'
        '\n'
        '¿Deseas descargar el modelo ahora?'
    ),
    'settings.language_label': 'Idioma',
    'settings.language_desc': 'Idioma de la interfaz · Se aplica de inmediato.',
    'settings.language_en': 'English',
    'settings.language_es': 'Español',
}

_CATALOGS = {
    "en": STRINGS_EN,
    "es": STRINGS_ES,
}

STRINGS = dict(STRINGS_EN)


def get_language() -> str:
    """Returns the active language code ('en' | 'es')."""
    return _CURRENT_LANGUAGE


def get_available_languages() -> dict[str, str]:
    """Returns mapping of available language codes to human-readable names."""
    return dict(LANGUAGES)


def set_language(lang_code: str):
    """Sets the active language and updates STRINGS in-place."""
    global _CURRENT_LANGUAGE
    if lang_code not in _CATALOGS:
        lang_code = DEFAULT_LANGUAGE
    _CURRENT_LANGUAGE = lang_code
    STRINGS.clear()
    STRINGS.update(_CATALOGS[lang_code])


def t(key: str, **kwargs) -> str:
    """Returns the localized string for `key`, falling back to English if missing."""
    catalog = _CATALOGS.get(_CURRENT_LANGUAGE, STRINGS_EN)
    text = catalog.get(key)
    if text is None:
        text = STRINGS_EN.get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
