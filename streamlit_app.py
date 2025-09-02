#!/usr/bin/env python3
"""
Streamlit To-Do List Application
A modern web-based to-do list manager with persistent storage.
"""

import streamlit as st
import json
import os
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

# Configure page
st.set_page_config(
    page_title="To-Do List Manager",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

class TodoApp:
    def __init__(self, filename: str = "streamlit_todos.json"):
        self.filename = filename
        if 'todos' not in st.session_state:
            st.session_state.todos = self.load_todos()
    
    def load_todos(self) -> List[Dict[str, Any]]:
        """Load todos from JSON file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                st.warning(f"Could not load {self.filename}. Starting with empty list.")
        return []
    
    def save_todos(self) -> None:
        """Save todos to JSON file."""
        try:
            with open(self.filename, 'w') as f:
                json.dump(st.session_state.todos, f, indent=2)
        except IOError:
            st.error(f"Could not save to {self.filename}")
    
    def add_todo(self, task: str, priority: str = "Medium", category: str = "Personal") -> None:
        """Add a new todo item."""
        if not task.strip():
            st.error("Task cannot be empty.")
            return
        
        # Generate new ID
        max_id = max([todo.get('id', 0) for todo in st.session_state.todos], default=0)
        
        todo = {
            "id": max_id + 1,
            "task": task.strip(),
            "completed": False,
            "priority": priority,
            "category": category,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "due_date": None
        }
        
        st.session_state.todos.append(todo)
        self.save_todos()
        st.success(f"✅ Added task: '{task}'")
    
    def complete_todo(self, task_id: int) -> None:
        """Mark a todo as completed."""
        for todo in st.session_state.todos:
            if todo["id"] == task_id:
                todo["completed"] = True
                todo["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_todos()
                st.success(f"✅ Completed task: '{todo['task']}'")
                st.rerun()
                break
    
    def delete_todo(self, task_id: int) -> None:
        """Delete a todo item."""
        original_count = len(st.session_state.todos)
        st.session_state.todos = [t for t in st.session_state.todos if t["id"] != task_id]
        
        if len(st.session_state.todos) < original_count:
            self.save_todos()
            st.success("🗑️ Task deleted successfully!")
            st.rerun()
    
    def update_priority(self, task_id: int, priority: str) -> None:
        """Update the priority of a task."""
        for todo in st.session_state.todos:
            if todo["id"] == task_id:
                todo["priority"] = priority
                self.save_todos()
                st.success(f"✅ Updated priority for '{todo['task']}' to {priority}")
                st.rerun()
                break
    
    def clear_completed(self) -> None:
        """Remove all completed tasks."""
        completed_count = len([t for t in st.session_state.todos if t["completed"]])
        if completed_count == 0:
            st.info("No completed tasks to clear.")
            return
        
        st.session_state.todos = [t for t in st.session_state.todos if not t["completed"]]
        self.save_todos()
        st.success(f"🧹 Cleared {completed_count} completed task(s)")
        st.rerun()
    
    def get_stats(self) -> Dict[str, int]:
        """Get task statistics."""
        total = len(st.session_state.todos)
        completed = len([t for t in st.session_state.todos if t["completed"]])
        pending = total - completed
        
        priority_counts = {"High": 0, "Medium": 0, "Low": 0}
        category_counts = {}
        
        for todo in st.session_state.todos:
            if not todo["completed"]:
                priority_counts[todo["priority"]] += 1
                category = todo.get("category", "Personal")
                category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "priority_counts": priority_counts,
            "category_counts": category_counts
        }


def main():
    # Initialize the app
    app = TodoApp()
    
    # Header
    st.title("📝 To-Do List Manager")
    st.markdown("Stay organized and productive with your personal task manager!")
    
    # Sidebar for adding tasks and filters
    with st.sidebar:
        st.header("➕ Add New Task")
        
        with st.form("add_task_form"):
            new_task = st.text_input("Task Description", placeholder="Enter your task...")
            
            col1, col2 = st.columns(2)
            with col1:
                priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)
            with col2:
                category = st.selectbox("Category", ["Personal", "Work", "Health", "Learning", "Shopping", "Other"])
            
            submit_button = st.form_submit_button("Add Task", type="primary")
            
            if submit_button and new_task:
                app.add_todo(new_task, priority, category)
        
        st.divider()
        
        # Filters
        st.header("🔍 Filters")
        show_completed = st.checkbox("Show completed tasks", value=True)
        
        filter_priority = st.multiselect(
            "Filter by Priority",
            ["High", "Medium", "Low"],
            default=["High", "Medium", "Low"]
        )
        
        filter_category = st.multiselect(
            "Filter by Category",
            ["Personal", "Work", "Health", "Learning", "Shopping", "Other"],
            default=["Personal", "Work", "Health", "Learning", "Shopping", "Other"]
        )
        
        st.divider()
        
        # Quick actions
        st.header("⚡ Quick Actions")
        if st.button("🧹 Clear Completed Tasks"):
            app.clear_completed()
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("📋 Your Tasks")
        
        # Filter tasks based on sidebar selections
        filtered_todos = []
        for todo in st.session_state.todos:
            if not show_completed and todo["completed"]:
                continue
            if todo["priority"] not in filter_priority:
                continue
            if todo.get("category", "Personal") not in filter_category:
                continue
            filtered_todos.append(todo)
        
        # Sort tasks: incomplete first, then by priority
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        filtered_todos.sort(key=lambda x: (x["completed"], priority_order.get(x["priority"], 1)))
        
        if not filtered_todos:
            st.info("No tasks match your current filters. Try adjusting the filters or add a new task!")
        else:
            # Display tasks
            for todo in filtered_todos:
                with st.container():
                    # Task row
                    task_col, priority_col, category_col, action_col = st.columns([3, 0.8, 0.8, 1.2])
                    
                    with task_col:
                        # Status and task text
                        if todo["completed"]:
                            st.markdown(f"✅ ~~{todo['task']}~~")
                            st.caption(f"Created: {todo['created_at']} | Completed: {todo.get('completed_at', 'N/A')}")
                        else:
                            st.markdown(f"⭕ **{todo['task']}**")
                            st.caption(f"Created: {todo['created_at']}")
                    
                    with priority_col:
                        priority_colors = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                        st.markdown(f"{priority_colors.get(todo['priority'], '⚪')} {todo['priority']}")
                    
                    with category_col:
                        st.markdown(f"📁 {todo.get('category', 'Personal')}")
                    
                    with action_col:
                        action_col1, action_col2 = st.columns(2)
                        
                        with action_col1:
                            if not todo["completed"]:
                                if st.button("✅", key=f"complete_{todo['id']}", help="Mark as complete"):
                                    app.complete_todo(todo['id'])
                        
                        with action_col2:
                            if st.button("🗑️", key=f"delete_{todo['id']}", help="Delete task"):
                                app.delete_todo(todo['id'])
                    
                    st.divider()
    
    with col2:
        st.header("📊 Statistics")
        
        stats = app.get_stats()
        
        # Task overview
        st.metric("Total Tasks", stats["total"])
        st.metric("Completed", stats["completed"])
        st.metric("Pending", stats["pending"])
        
        if stats["pending"] > 0:
            st.subheader("Pending by Priority")
            for priority, count in stats["priority_counts"].items():
                if count > 0:
                    color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}[priority]
                    st.write(f"{color} {priority}: {count}")
            
            if stats["category_counts"]:
                st.subheader("Tasks by Category")
                for category, count in stats["category_counts"].items():
                    st.write(f"📁 {category}: {count}")
        
        # Progress bar
        if stats["total"] > 0:
            progress = stats["completed"] / stats["total"]
            st.progress(progress)
            st.caption(f"Progress: {progress:.1%}")
        
        # Export data
        st.subheader("📤 Export")
        if st.session_state.todos:
            # Create DataFrame for export
            df = pd.DataFrame(st.session_state.todos)
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "todos.csv",
                "text/csv",
                key="download-csv"
            )


if __name__ == "__main__":
    main()
