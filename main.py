"""
Interactive CLI for Email Task Extraction
Run this to process emails and view results
"""
import json
from task_extractor import process_email


def print_separator():
    print("\n" + "="*80 + "\n")


def print_task(task, index):
    """Pretty print a single task"""
    confidence = task['confidence_metrics']
    status_emoji = {
        'auto_approved': '✅',
        'needs_review': '⚠️',
        'needs_urgent_review': '🔴'
    }
    
    emoji = status_emoji.get(task['review_status'], '❓')
    
    print(f"{emoji} Task {index + 1}: {task['task_description']}")
    print(f"   Assignee: {task['assignee']}")
    print(f"   Deadline: {task.get('deadline', 'Not specified')}")
    print(f"   Priority: {task['priority']}")
    print(f"   Confidence: {confidence['final_confidence']:.2f} (LLM: {confidence['llm_confidence']:.2f})")
    print(f"   Status: {task['review_status'].replace('_', ' ').title()}")
    
    if confidence['adjustments']:
        print(f"   Adjustments: {', '.join(confidence['adjustments'])}")
    
    print()


def main():
    print("="*80)
    print("EMAIL TASK EXTRACTOR - Interactive Mode")
    print("="*80)
    print("\nThis tool extracts tasks from emails using AI and assigns confidence scores.")
    print("Tasks with confidence < 0.7 are flagged for human review.\n")
    
    while True:
        print("\nOptions:")
        print("1. Process a sample email")
        print("2. Enter your own email text")
        print("3. Process email from file")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            # Sample email
            email = """
Subject: Q1 Deliverables and Team Meeting

Hi team,

I need everyone to complete the following by end of March:

1. Sarah - Please finalize the marketing analysis report by March 20th. This is critical for our board presentation.

2. The engineering team should review and approve the new API documentation. Not sure exactly when, but ideally before the end of the quarter.

3. Mike, can you schedule a team retrospective meeting? Maybe sometime in the first week of April?

4. We also need someone to update the client database, but I haven't decided who yet.

Let me know if you have any questions.

Best,
Jennifer
Manager, Product Team
            """
            sender = "jennifer@company.com"
            
        elif choice == '2':
            print("\nPaste your email content (press Ctrl+D or Ctrl+Z when done):")
            print("-" * 80)
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            email = '\n'.join(lines)
            sender = input("\nEmail sender (optional, press Enter to skip): ").strip() or None
            
        elif choice == '3':
            filepath = input("\nEnter path to email file: ").strip()
            try:
                with open(filepath, 'r') as f:
                    email = f.read()
                sender = input("Email sender (optional, press Enter to skip): ").strip() or None
            except FileNotFoundError:
                print(f"❌ File not found: {filepath}")
                continue
            except Exception as e:
                print(f"❌ Error reading file: {e}")
                continue
                
        elif choice == '4':
            print("\nGoodbye!")
            break
            
        else:
            print("❌ Invalid option. Please select 1-4.")
            continue
        
        # Process the email
        print_separator()
        print("🔍 Processing email with AI...")
        print_separator()
        
        try:
            result = process_email(email, sender)
            
            if not result['success']:
                print(f"❌ Error: {result['error']}\n")
                continue
            
            # Display results
            summary = result['queue_summary']
            print("📊 EXTRACTION SUMMARY")
            print(f"   Total tasks extracted: {summary['total_tasks']}")
            print(f"   ✅ Auto-approved: {summary['auto_approved']}")
            print(f"   ⚠️  Need review: {summary['standard_review']}")
            print(f"   🔴 Need urgent review: {summary['high_priority_review']}")
            
            print_separator()
            print("📋 EXTRACTED TASKS")
            print_separator()
            
            for i, task in enumerate(result['processed_tasks']):
                print_task(task, i)
            
            # Show ambiguities
            if result['extraction_result'].get('ambiguities'):
                print_separator()
                print("⚠️  AMBIGUITIES DETECTED")
                print_separator()
                for ambiguity in result['extraction_result']['ambiguities']:
                    print(f"  • {ambiguity}")
                print()
            
            # Option to save
            save = input("\nSave results to JSON file? (y/n): ").strip().lower()
            if save == 'y':
                filename = f"extraction_result_{result['extraction_result']['extraction_timestamp'].replace(':', '-')}.json"
                with open(filename, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                print(f"✅ Saved to {filename}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
