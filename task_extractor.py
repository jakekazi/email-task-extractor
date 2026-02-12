"""
Email Task Extractor - Main Module
Extracts structured tasks from unstructured emails using LLM
"""
import json
from datetime import datetime
from typing import List, Dict, Any
import anthropic
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


class TaskExtractor:
    """Handles LLM-based task extraction from emails"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Set it in .env file or pass as argument")
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def extract_tasks(self, email_content: str, sender: str = None) -> Dict[str, Any]:
        """
        Extract tasks from email content using Claude
        
        Args:
            email_content: The body of the email
            sender: Email sender (optional, helps with context)
            
        Returns:
            Dictionary containing extracted tasks and metadata
        """
        prompt = self._build_extraction_prompt(email_content, sender)
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0,  # Lower temperature for more consistent extraction
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Parse JSON response
            result = json.loads(response_text)
            
            # Add metadata
            result['extraction_timestamp'] = datetime.now().isoformat()
            result['model_used'] = 'claude-sonnet-4-20250514'
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response as JSON: {e}")
            print(f"Raw response: {response_text}")
            return self._create_error_response("Invalid JSON response from LLM")
        except Exception as e:
            print(f"Error during task extraction: {e}")
            return self._create_error_response(str(e))
    
    def _build_extraction_prompt(self, email_content: str, sender: str = None) -> str:
        """Build the prompt for task extraction"""
        sender_context = f"\nEmail from: {sender}" if sender else ""
        
        return f"""Analyze this email and extract all tasks, requests, deadlines, and action items.{sender_context}

For each task, provide:
- task_description: Clear, actionable description of what needs to be done
- assignee: Person responsible (if mentioned, otherwise "unspecified")
- deadline: Extracted deadline in ISO format (YYYY-MM-DD) or null if not specified
- priority: "high", "medium", or "low" based on context and urgency indicators
- confidence_score: Your confidence in this extraction (0.0 to 1.0)
  * 1.0 = Completely explicit and clear
  * 0.7-0.9 = Clear but may need minor clarification
  * 0.5-0.7 = Some ambiguity or missing information
  * Below 0.5 = Highly uncertain or vague
- reasoning: Brief explanation of the confidence score (what's clear, what's ambiguous)

Guidelines for confidence scoring:
- High confidence (0.8-1.0): Task is explicitly stated with clear deadline and assignee
- Medium confidence (0.5-0.7): Task is clear but deadline or assignee is implied/missing
- Low confidence (0.0-0.5): Task is vague, multiple interpretations possible, or inferred from context

Email content:
{email_content}

Respond ONLY with valid JSON in this exact format (no markdown, no explanation):
{{
  "tasks": [
    {{
      "task_description": "Complete the quarterly report",
      "assignee": "John Smith",
      "deadline": "2024-03-15",
      "priority": "high",
      "confidence_score": 0.95,
      "reasoning": "Task, assignee, and deadline are all explicitly stated"
    }}
  ],
  "overall_confidence": 0.85,
  "ambiguities": ["List any unclear aspects that need human review"]
}}"""
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create a standardized error response"""
        return {
            'tasks': [],
            'overall_confidence': 0.0,
            'ambiguities': [error_message],
            'extraction_timestamp': datetime.now().isoformat(),
            'error': True
        }


class ConfidenceCalculator:
    """Calculates and adjusts confidence scores"""
    
    @staticmethod
    def calculate_final_confidence(task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate final confidence with rule-based adjustments
        
        Args:
            task: Task dictionary with LLM confidence score
            
        Returns:
            Dictionary with detailed confidence metrics
        """
        llm_confidence = task.get('confidence_score', 0.0)
        penalties = 0.0
        adjustments = []
        
        # Rule-based penalties
        if not task.get('deadline'):
            penalties += 0.15
            adjustments.append("No deadline specified (-0.15)")
        
        if task.get('assignee') == 'unspecified':
            penalties += 0.20
            adjustments.append("Assignee not specified (-0.20)")
        
        # Check for vague task descriptions
        description = task.get('task_description', '').lower()
        vague_words = ['maybe', 'might', 'possibly', 'consider', 'think about']
        if any(word in description for word in vague_words):
            penalties += 0.10
            adjustments.append("Vague language detected (-0.10)")
        
        final_confidence = max(0.0, min(1.0, llm_confidence - penalties))
        
        return {
            'llm_confidence': llm_confidence,
            'rule_penalties': penalties,
            'final_confidence': final_confidence,
            'adjustments': adjustments,
            'needs_review': final_confidence < 0.7
        }


class TaskReviewQueue:
    """Manages routing of tasks based on confidence scores"""
    
    def __init__(self, 
                 auto_approve_threshold: float = 0.7,
                 high_priority_threshold: float = 0.5):
        self.auto_approve_threshold = auto_approve_threshold
        self.high_priority_threshold = high_priority_threshold
        
        self.auto_approved: List[Dict] = []
        self.standard_review: List[Dict] = []
        self.high_priority_review: List[Dict] = []
    
    def route_task(self, task: Dict[str, Any], confidence_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route task to appropriate queue based on confidence
        
        Args:
            task: The extracted task
            confidence_metrics: Confidence calculation results
            
        Returns:
            Task with added routing metadata
        """
        final_confidence = confidence_metrics['final_confidence']
        
        task_with_metadata = {
            **task,
            'confidence_metrics': confidence_metrics,
            'routed_at': datetime.now().isoformat()
        }
        
        if final_confidence >= self.auto_approve_threshold:
            task_with_metadata['review_status'] = 'auto_approved'
            task_with_metadata['queue'] = 'auto_approved'
            self.auto_approved.append(task_with_metadata)
        elif final_confidence >= self.high_priority_threshold:
            task_with_metadata['review_status'] = 'needs_review'
            task_with_metadata['queue'] = 'standard_review'
            self.standard_review.append(task_with_metadata)
        else:
            task_with_metadata['review_status'] = 'needs_urgent_review'
            task_with_metadata['queue'] = 'high_priority_review'
            self.high_priority_review.append(task_with_metadata)
        
        return task_with_metadata
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of queue status"""
        return {
            'total_tasks': len(self.auto_approved) + len(self.standard_review) + len(self.high_priority_review),
            'auto_approved': len(self.auto_approved),
            'standard_review': len(self.standard_review),
            'high_priority_review': len(self.high_priority_review)
        }
    
    def get_review_tasks(self) -> List[Dict]:
        """Get all tasks that need review, prioritized"""
        return self.high_priority_review + self.standard_review


def process_email(email_content: str, sender: str = None, api_key: str = None) -> Dict[str, Any]:
    """
    Main pipeline function to process an email
    
    Args:
        email_content: The email body text
        sender: Email sender (optional)
        api_key: Anthropic API key (optional, can be in .env)
        
    Returns:
        Processing results including routed tasks and summary
    """
    # Initialize components
    extractor = TaskExtractor(api_key)
    calculator = ConfidenceCalculator()
    queue = TaskReviewQueue()
    
    # Step 1: Extract tasks
    extraction_result = extractor.extract_tasks(email_content, sender)
    
    if extraction_result.get('error'):
        return {
            'success': False,
            'error': extraction_result.get('ambiguities', ['Unknown error'])[0],
            'extraction_result': extraction_result
        }
    
    # Step 2: Process each task
    processed_tasks = []
    
    for task in extraction_result.get('tasks', []):
        # Calculate confidence
        confidence_metrics = calculator.calculate_final_confidence(task)
        
        # Route to queue
        routed_task = queue.route_task(task, confidence_metrics)
        processed_tasks.append(routed_task)
    
    # Step 3: Prepare results
    return {
        'success': True,
        'extraction_result': extraction_result,
        'processed_tasks': processed_tasks,
        'queue_summary': queue.get_summary(),
        'auto_approved_tasks': queue.auto_approved,
        'review_tasks': queue.get_review_tasks()
    }


if __name__ == "__main__":
    # Quick test if run directly
    test_email = """
    Hi team,
    
    Can you please finish the Q1 report by March 15th? John should handle the financial section.
    
    Also, we might want to schedule a meeting sometime next week to discuss the project timeline.
    
    Thanks!
    """
    
    print("Testing email task extraction...\n")
    result = process_email(test_email, sender="manager@company.com")
    
    if result['success']:
        print(f"Extracted {len(result['processed_tasks'])} tasks:")
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"Error: {result['error']}")
