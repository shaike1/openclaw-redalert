#!/usr/bin/env python3
"""
Google Tasks API Helper
Uses Service Account for authentication
"""

import os
import sys
from datetime import datetime, timedelta

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("❌ Missing libraries. Installing...")
    os.system("pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

# Service Account credentials
SERVICE_ACCOUNT_FILE = '/tmp/gogcli-service-account.json'
SCOPES = ['https://www.googleapis.com/auth/tasks']

def get_tasks_service():
    """Get authenticated Tasks service"""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('tasks', 'v1', credentials=credentials)
    return service

def list_tasklists():
    """List all task lists"""
    service = get_tasks_service()
    
    tasklists = service.tasklists().list().execute()
    items = tasklists.get('items', [])
    
    if not items:
        print('📭 No task lists found.')
        print('💡 Creating a default task list...')
        result = service.tasklists().insert(body={
            'title': 'My Tasks'
        }).execute()
        print(f"✅ Created default task list: {result['title']}")
        return [result]
    
    print(f"📚 Found {len(items)} task lists:\n")
    for i, tl in enumerate(items, 1):
        print(f"{i}. 📋 {tl['title']}")
        print(f"   🆔 ID: {tl['id']}")
        print()
    
    return items

def list_tasks(tasklist_id='@default'):
    """List all tasks in a task list"""
    service = get_tasks_service()
    
    tasks = service.tasks().list(tasklist=tasklist_id).execute()
    items = tasks.get('items', [])
    
    if not items:
        print('📭 No tasks found.')
    else:
        print(f"✅ Found {len(items)} tasks:\n")
        for i, task in enumerate(items, 1):
            title = task.get('title', '(No title)')
            status = task.get('status', 'needsAction')
            due = task.get('due', '')
            
            status_emoji = '✅' if status == 'completed' else '⏳'
            due_str = f" 📅 {due[:10]}" if due else ""
            
            print(f"{i}. {status_emoji} {title}{due_str}")
            print(f"   🆔 ID: {task['id']}")
            print()
    
    return items

def create_task(title, tasklist_id='@default', notes='', due_date=None):
    """Create a new task"""
    service = get_tasks_service()
    
    task = {
        'title': title,
        'status': 'needsAction'
    }
    
    if notes:
        task['notes'] = notes
    
    if due_date:
        # due_date should be YYYY-MM-DD
        task['due'] = f"{due_date}T00:00:00Z"
    
    result = service.tasks().insert(tasklist=tasklist_id, body=task).execute()
    print(f"✅ Task created: {result['title']}")
    return result

def complete_task(task_id, tasklist_id='@default'):
    """Mark a task as completed"""
    service = get_tasks_service()
    
    # First get the task
    task = service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
    
    # Update status
    task['status'] = 'completed'
    task['completed'] = datetime.utcnow().isoformat() + 'Z'
    
    result = service.tasks().update(
        tasklist=tasklist_id,
        task=task_id,
        body=task
    ).execute()
    
    print(f"✅ Task completed: {result['title']}")
    return result

def uncomplete_task(task_id, tasklist_id='@default'):
    """Mark a task as not completed"""
    service = get_tasks_service()
    
    # First get the task
    task = service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
    
    # Update status
    task['status'] = 'needsAction'
    if 'completed' in task:
        del task['completed']
    
    result = service.tasks().update(
        tasklist=tasklist_id,
        task=task_id,
        body=task
    ).execute()
    
    print(f"✅ Task uncompleted: {result['title']}")
    return result

def delete_task(task_id, tasklist_id='@default'):
    """Delete a task"""
    service = get_tasks_service()
    
    try:
        service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
        print(f"✅ Task deleted successfully!")
        return True
    except Exception as e:
        print(f"❌ Error deleting task: {e}")
        return False

def update_task(task_id, tasklist_id='@default', title=None, notes=None):
    """Update a task"""
    service = get_tasks_service()
    
    # First get the task
    task = service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
    
    # Update fields
    if title:
        task['title'] = title
    if notes:
        task['notes'] = notes
    
    result = service.tasks().update(
        tasklist=tasklist_id,
        task=task_id,
        body=task
    ).execute()
    
    print(f"✅ Task updated: {result['title']}")
    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("""
🤖 Google Tasks API Helper

Usage:
  python3 google_tasks.py lists                    - List all task lists
  python3 google_tasks.py tasks [list_id]          - List tasks in a list
  python3 google_tasks.py create <title> [due]     - Create a task
  python3 google_tasks.py complete <task_id>       - Mark task as completed
  python3 google_tasks.py uncomplete <task_id>     - Mark task as not completed
  python3 google_tasks.py delete <task_id>         - Delete a task
  python3 google_tasks.py update <task_id> <field> <value> - Update task

Examples:
  python3 google_tasks.py lists
  python3 google_tasks.py tasks
  python3 google_tasks.py create "Buy milk" "2026-02-25"
  python3 google_tasks.py complete <task_id>
  python3 google_tasks.py delete <task_id>
  python3 google_tasks.py update <task_id> title "New title"

Update fields:
  title <text>
  notes <text>
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'lists':
        list_tasklists()
    
    elif command == 'tasks':
        tasklist_id = sys.argv[2] if len(sys.argv) > 2 else '@default'
        list_tasks(tasklist_id)
    
    elif command == 'create':
        if len(sys.argv) < 3:
            print("❌ Usage: python3 google_tasks.py create <title> [due_date]")
            sys.exit(1)
        title = sys.argv[2]
        due = sys.argv[3] if len(sys.argv) > 3 else None
        create_task(title, due_date=due)
    
    elif command == 'complete':
        if len(sys.argv) < 3:
            print("❌ Usage: python3 google_tasks.py complete <task_id>")
            sys.exit(1)
        task_id = sys.argv[2]
        complete_task(task_id)
    
    elif command == 'uncomplete':
        if len(sys.argv) < 3:
            print("❌ Usage: python3 google_tasks.py uncomplete <task_id>")
            sys.exit(1)
        task_id = sys.argv[2]
        uncomplete_task(task_id)
    
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("❌ Usage: python3 google_tasks.py delete <task_id>")
            sys.exit(1)
        task_id = sys.argv[2]
        delete_task(task_id)
    
    elif command == 'update':
        if len(sys.argv) < 5:
            print("❌ Usage: python3 google_tasks.py update <task_id> <field> <value>")
            print("   Fields: title, notes")
            sys.exit(1)
        
        task_id = sys.argv[2]
        field = sys.argv[3]
        value = sys.argv[4]
        
        if field == 'title':
            update_task(task_id, title=value)
        elif field == 'notes':
            update_task(task_id, notes=value)
        else:
            print(f"❌ Unknown field: {field}")
            sys.exit(1)
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
