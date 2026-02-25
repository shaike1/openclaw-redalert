#!/usr/bin/env python3
"""
Enhanced homework parser that distinguishes between past classes and homework
"""

import json
import re
from datetime import datetime

def parse_homework_enhanced(raw_text):
    """Parse homework text and distinguish between past classes and actual homework"""
    
    # Split into lines and clean up
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    
    # Initialize structure
    structure = {
        'classes_held': [],  # שיעורים שכבר עברו
        'homework': [],     # שיעורי בית
        'notes': []         # הערות כלליות
    }
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip "שיעורי בית" header
        if line == "שיעורי בית":
            i += 1
            continue
            
        # Check if this is a class entry
        if is_class_line(line):
            class_info = parse_class_entry(lines, i)
            if class_info:
                structure['classes_held'].append(class_info)
                i = class_info['end_index']
                continue
                
        # Check for homework assignment
        elif "שיעורי בית:" in line:
            homework_info = parse_homework_line(line)
            if homework_info:
                structure['homework'].append(homework_info)
                
        # Add as note
        else:
            structure['notes'].append(line)
            
        i += 1
    
    return structure

def is_class_line(line):
    """Check if line indicates a class entry"""
    patterns = [
        r'שיעור \d+',      # שיעור + number
        r'מקצוע: .*',      # מקצוע:
        r'מורה: .*',      # מורה:
        r'התקיים',        # התקיים
        r'נושא שיעור: .*', # נושא שיעור:
    ]
    
    return any(re.search(pattern, line) for pattern in patterns)

def parse_class_entry(lines, start_index):
    """Parse a class entry and extract all relevant info"""
    class_info = {
        'subject': None,
        'teacher': None,
        'number': None,
        'status': 'past',  # "התקיים" means it was held
        'topic': None,
        'homework_assigned': None,
        'end_index': start_index
    }
    
    i = start_index
    lines_counted = 0
    
    while i < len(lines) and lines_counted < 10:  # Max 10 lines per class
        line = lines[i]
        
        # Extract subject
        if not class_info['subject'] and not line.startswith('שיעור'):
            class_info['subject'] = line
            
        # Extract class number
        if 'שיעור' in line and not class_info['number']:
            match = re.search(r'שיעור (\d+)', line)
            if match:
                class_info['number'] = match.group(1)
                
        # Extract teacher
        if not class_info['teacher']:
            if 'ביטון' in line:
                class_info['teacher'] = 'ביטון אסתר'
            elif 'פלד' in line:
                class_info['teacher'] = 'פלד גיל'
            elif 'רומנובסקי' in line:
                class_info['teacher'] = 'רומנובסקי סיגל'
                
        # Check if class was held
        if 'התקיים' in line:
            class_info['status'] = 'past'
            
        # Extract topic
        if 'נושא שיעור:' in line:
            topic = line.replace('נושא שיעור:', '').strip()
            class_info['topic'] = topic
            
        # Check for homework
        if 'שיעורי בית:' in line:
            homework = line.replace('שיעורי בית:', '').strip()
            if homework and homework != 'לא הוזן':
                class_info['homework_assigned'] = homework
                class_info['status'] = 'with_homework'
            else:
                class_info['status'] = 'no_homework'
                
        i += 1
        lines_counted += 1
        
        # Stop if we see next class or new section
        if i < len(lines) and lines[i] in ['שיעורי בית', 'מדעים', 'עברית', 'תורה', 'כישורי חיים']:
            break
            
    class_info['end_index'] = i
    return class_info

def parse_homework_line(line):
    """Parse a homework assignment line"""
    homework_info = {
        'type': 'homework',
        'subject': None,
        'description': None,
        'pages': None,
        'exercises': None,
        'status': 'not_assigned'  # not_assigned, assigned, completed
    }
    
    # Extract homework text
    homework_text = line.replace('שיעורי בית:', '').strip()
    
    if homework_text == 'לא הוזן':
        homework_info['status'] = 'not_assigned'
    else:
        homework_info['status'] = 'assigned'
        homework_info['description'] = homework_text
        
        # Try to extract pages/exercises
        page_match = re.search(r'עמוד[י]? (\d+)', homework_text)
        if page_match:
            homework_info['pages'] = page_match.group(1)
            
        exercise_match = re.search(r'תרגיל[י]? (\d+)', homework_text)
        if exercise_match:
            homework_info['exercises'] = exercise_match.group(1)
    
    return homework_info

def format_enhanced_homework(structure):
    """Format the parsed homework for display"""
    formatted = ""
    
    # Classes held
    if structure['classes_held']:
        formatted += "📚 **שיעורים שהיום:**\n\n"
        for cls in structure['classes_held']:
            status_icon = "✅" if cls['status'] == 'past' else "📝"
            formatted += f"{status_icon} **{cls['subject']}** (שיעור {cls['number']})\n"
            formatted += f"   🎓 {cls['topic']}\n"
            
            if cls['homework_assigned']:
                formatted += f"   📝 **שיעורי בית:** {cls['homework_assigned']}\n"
            else:
                formatted += f"   📋 לא הוזן שיעור בית\n"
            formatted += "\n"
    
    # Homework assignments
    if structure['homework']:
        formatted += "📝 **שיעורי בית לעשות:**\n\n"
        for hw in structure['homework']:
            if hw['status'] == 'assigned':
                formatted += f"   ✅ {hw['description']}\n"
            else:
                formatted += f"   ❌ לא הוזן שיעור בית\n"
        formatted += "\n"
    
    # Notes
    if structure['notes']:
        formatted += "📋 **הערות:**\n"
        for note in structure['notes'][:5]:  # Show first 5 notes
            formatted += f"   • {note}\n"
    
    return formatted.strip()

# Test with current data
if __name__ == "__main__":
    # Load current homework data
    with open('/tmp/webtop_homework_REDACTED_STUDENT_1.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    raw_text = data['homework'][0]['full_text']
    
    # Parse with enhanced parser
    structure = parse_homework_enhanced(raw_text)
    
    # Format and display
    formatted = format_enhanced_homework(structure)
    
    print("🎓 Enhanced Homework Parser")
    print("=" * 50)
    print(formatted)
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print(f"   Classes held: {len(structure['classes_held'])}")
    print(f"   Homework items: {len(structure['homework'])}")
    print(f"   Notes: {len(structure['notes'])}")