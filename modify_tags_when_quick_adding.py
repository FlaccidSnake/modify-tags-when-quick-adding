# -*- coding: utf-8 -*-
"""
Anki Add-on: Modify Tags When Quick Adding
Add a context menu item to tag sidebar for modifying and adding tags to selected notes.
Copyright: 2026
License: GNU AGPLv3 or later <https://www.gnu.org/licenses/agpl.html>
"""
from aqt.qt import *
from aqt.utils import tooltip
from aqt.tagedit import TagEdit
from aqt import gui_hooks
from aqt.browser import SidebarItemType

def getModifiedTag(parent, col, tag):
    """Show dialog with tag that can be modified before adding"""
    te = TagEdit(parent)
    te.setCol(col)
    
    # Create dialog
    dialog = QDialog(parent)
    dialog.setWindowTitle("Add tag")
    dialog.setMinimumWidth(400)
    
    layout = QVBoxLayout()
    
    # Add bold label
    label = QLabel("<b>Modify tag before adding:</b>")
    layout.addWidget(label)
    
    # Add tag edit widget
    te.setText(tag)
    te.selectAll()
    layout.addWidget(te)
    
    # Add buttons
    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    buttonBox.accepted.connect(dialog.accept)
    buttonBox.rejected.connect(dialog.reject)
    layout.addWidget(buttonBox)
    
    dialog.setLayout(layout)
    
    # Show dialog and return result
    result = dialog.exec()
    te.hideCompleter()
    
    if result == QDialog.DialogCode.Accepted:
        return (te.text(), True)
    else:
        return ("", False)

def modifyAndAddTag(sidebar, tag):
    """Modify the clicked tag and add it to selected notes"""
    browser = sidebar.browser
    mw = browser.mw
    selected = browser.selectedNotes()
    
    if not selected:
        tooltip("No cards selected.", period=2000)
        return
    
    # Show dialog with the tag that can be modified
    (modifiedTag, confirmed) = getModifiedTag(browser, mw.col, tag)
    
    if not confirmed or not modifiedTag.strip():
        return
    
    # Add the modified tag to all selected notes
    mw.checkpoint("add modified tag")
    mw.progress.start()
    browser.model.beginReset()
    
    for nid in selected:
        note = mw.col.getNote(nid)
        note.addTag(modifiedTag)
        note.flush()
    
    browser.model.endReset()
    mw.requireReset()
    mw.progress.finish()
    mw.reset()
    
    tooltip(f"Tag '{modifiedTag}' added to {len(selected)} note(s).")

def onSidebarContextMenu(sidebar, menu, item, index):
    """Add context menu item to tag sidebar"""
    # Check if this is a tag item
    if item.item_type == SidebarItemType.TAG:
        tag = item.full_name
        
        # Insert action as third item (after first two existing actions)
        actions = menu.actions()
        if len(actions) >= 2:
            # Insert after the second action
            action = QAction("Modify and add to selected notes", menu)
            action.triggered.connect(lambda: modifyAndAddTag(sidebar, tag))
            menu.insertAction(actions[2] if len(actions) > 2 else None, action)
        else:
            # Fallback: add at end if menu has fewer than 2 actions
            menu.addSeparator()
            action = menu.addAction("Modify and add to selected notes")
            action.triggered.connect(lambda: modifyAndAddTag(sidebar, tag))

# Register the hook directly
gui_hooks.browser_sidebar_will_show_context_menu.append(onSidebarContextMenu)
