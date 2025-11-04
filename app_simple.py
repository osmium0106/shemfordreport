from flask import Flask, render_template, request, jsonify
import requests
import csv
from io import StringIO
from datetime import datetime

app = Flask(__name__)

class GoogleSheetsConnector:
    def __init__(self):
        # Dictionary to store URLs for each class - will be populated with your sheet URLs
        self.class_sheet_urls = {
            # Will be populated with your individual sheet URLs
            # '1B': 'https://docs.google.com/spreadsheets/d/e/...',
            # '1C': 'https://docs.google.com/spreadsheets/d/e/...',
            # etc.
        }
        print("✅ Google Sheets connector initialized - ready for multiple class URLs!")
    
    def add_class_sheet_url(self, class_name, sheet_url):
        """Add a published sheet URL for a specific class"""
        self.class_sheet_urls[class_name] = sheet_url
        print(f"📋 Added sheet URL for class {class_name}")
    
    def get_sheet_data_for_class(self, class_name):
        """Get data from the published sheet for a specific class"""
        try:
            if class_name not in self.class_sheet_urls:
                print(f"❌ No sheet URL configured for class {class_name}")
                return []
                
            sheet_url = self.class_sheet_urls[class_name]
            response = requests.get(sheet_url, timeout=10)
            
            if response.status_code == 200:
                csv_data = csv.reader(StringIO(response.text))
                data = list(csv_data)
                print(f"✅ Retrieved {len(data)} rows for class {class_name}")
                return data
            else:
                print(f"❌ Failed to get data for class {class_name}: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting data for class {class_name}: {e}")
            return []
    
    def get_classes(self):
        """Get list of available classes"""
        classes = list(self.class_sheet_urls.keys())
        print(f"📚 Available classes: {classes}")
        return sorted(classes, key=lambda x: (int(x[:-1]), x[-1]) if len(x) > 1 else (0, x))
    
    def get_students_by_class(self, class_name):
        """Get students from a specific class sheet"""
        try:
            data = self.get_sheet_data_for_class(class_name)
            
            if len(data) < 4:  # Need at least: class row, header row, sub-header row, and data
                print(f"⚠️  Insufficient data rows for class {class_name}")
                return []
            
            students = []
            
            # All classes now use multi-subject detection for consistency
            # For single-subject sheets, we'll create a single "Subject" tab
            subject_sections = []
            for i, row in enumerate(data):
                if len(row) > 0 and str(row[0]).strip() == 'Class':
                    subject_sections.append(i)
            
            if len(subject_sections) >= 1:
                # Use the first section (Maths) to get the student list
                first_section_start = subject_sections[0]
                
                # Find header row for this section
                header_row_idx = None
                for i in range(first_section_start, min(first_section_start + 5, len(data))):
                    if i < len(data) and len(data[i]) > 0 and 'Roll No.' in str(data[i][0]):
                        header_row_idx = i
                        break
                
                if header_row_idx is not None:
                    data_start_row = header_row_idx + 2
                    # Extract students only from first section
                    for row_idx in range(data_start_row, len(data)):
                        if row_idx < len(data) and len(data[row_idx]) >= 2:
                            # Stop if we hit another subject section
                            if str(data[row_idx][0]).strip() == 'Class':
                                break
                            
                            roll_no = str(data[row_idx][0]).strip()
                            if roll_no and roll_no.isdigit():
                                students.append({
                                    'Roll Number': roll_no,
                                    'Name': str(data[row_idx][1]).strip() if len(data[row_idx]) > 1 else ''
                                })
            else:
                # Single subject data - treat as one subject for consistency
                # Find the row that contains "Roll No." - should be row 2 (index 1)
                header_row_idx = 1
                for i, row in enumerate(data[:4]):
                    if len(row) > 0 and 'Roll No.' in str(row[0]):
                        header_row_idx = i
                        break
                
                # Data starts after the sub-header row
                data_start_row = header_row_idx + 2
                
                # Extract student data
                for row in data[data_start_row:]:
                    if len(row) >= 2 and str(row[0]).strip():
                        roll_no = str(row[0]).strip()
                        if roll_no and roll_no.isdigit():
                            students.append({
                                'Roll Number': roll_no,
                                'Name': str(row[1]).strip() if len(row) > 1 else ''
                            })
            
            print(f"📋 Found {len(students)} students in class {class_name}")
            return sorted(students, key=lambda x: int(x.get('Roll Number', 0)))
            
        except Exception as e:
            print(f"Error getting students for class {class_name}: {e}")
            return []
    
    def calculate_topic_ranks(self, class_name):
        """Calculate ranks for all topics in a class"""
        try:
            data = self.get_sheet_data_for_class(class_name)
            
            if len(data) < 4:
                return {}
            
            # Find header and data rows
            header_row_idx = 1
            for i, row in enumerate(data[:4]):
                if len(row) > 0 and 'Roll No.' in str(row[0]):
                    header_row_idx = i
                    break
            
            headers = data[header_row_idx]
            data_start_row = header_row_idx + 2
            
            # Collect all student marks for each topic
            topic_marks = {}  # {topic_name: [(roll_no, marks), ...]}
            
            # Process each topic from headers
            i = 2
            while i < len(headers):
                topic_header = headers[i].strip() if i < len(headers) else ''
                
                if topic_header and topic_header.startswith('Topic'):
                    topic_name = topic_header
                    topic_marks[topic_name] = []
                    
                    # Collect marks for this topic from all students
                    for row in data[data_start_row:]:
                        if len(row) > 0 and str(row[0]).strip():
                            roll_no = str(row[0]).strip()
                            marks_val = str(row[i + 1]).strip() if i + 1 < len(row) and row[i + 1] else '0'
                            
                            # Only include if marks is numeric
                            if marks_val and marks_val.replace('.','').isdigit():
                                topic_marks[topic_name].append((roll_no, float(marks_val)))
                    
                    i += 2
                else:
                    i += 1
            
            # Calculate ranks for each topic
            topic_ranks = {}  # {topic_name: {roll_no: rank}}
            
            for topic_name, marks_list in topic_marks.items():
                if not marks_list:
                    continue
                
                # Sort by marks in descending order (highest first)
                sorted_marks = sorted(marks_list, key=lambda x: x[1], reverse=True)
                
                # Calculate ranks with ties
                ranks = {}
                current_rank = 1
                
                for i, (roll_no, marks) in enumerate(sorted_marks):
                    if i > 0 and marks < sorted_marks[i-1][1]:
                        # Different marks, update rank
                        current_rank = i + 1
                    ranks[roll_no] = current_rank
                
                topic_ranks[topic_name] = ranks
            
            return topic_ranks
            
        except Exception as e:
            print(f"Error calculating topic ranks: {e}")
            return {}
    
    def calculate_subject_topic_ranks(self, data, subject_name, subject_start_row):
        """Calculate ranks for topics within a specific subject"""
        try:
            # Find header row for this subject
            header_row_idx = None
            for i in range(subject_start_row, min(subject_start_row + 5, len(data))):
                if i < len(data) and len(data[i]) > 0 and 'Roll No.' in str(data[i][0]):
                    header_row_idx = i
                    break
            
            if header_row_idx is None:
                return {}
            
            headers = data[header_row_idx]
            data_start_row = header_row_idx + 2
            
            # Collect all student marks for each topic in this subject
            topic_marks = {}  # {topic_name: [(roll_no, marks), ...]}
            
            # Process each topic from headers
            i = 2
            while i < len(headers):
                topic_header = headers[i].strip() if i < len(headers) else ''
                
                if topic_header and topic_header.startswith('Topic'):
                    topic_name = topic_header
                    topic_marks[topic_name] = []
                    
                    # Collect marks for this topic from all students
                    for row_idx in range(data_start_row, len(data)):
                        if row_idx < len(data) and len(data[row_idx]) > 0:
                            # Stop if we hit another subject
                            if str(data[row_idx][0]).strip() and 'Class' in str(data[row_idx][0]):
                                break
                            
                            roll_no = str(data[row_idx][0]).strip()
                            if roll_no and roll_no.isdigit():
                                marks_val = str(data[row_idx][i + 1]).strip() if i + 1 < len(data[row_idx]) and data[row_idx][i + 1] else '0'
                                
                                # Only include if marks is numeric
                                if marks_val and marks_val.replace('.','').isdigit():
                                    topic_marks[topic_name].append((roll_no, float(marks_val)))
                    
                    i += 2
                else:
                    i += 1
            
            # Calculate ranks for each topic
            topic_ranks = {}  # {topic_name: {roll_no: rank}}
            
            for topic_name, marks_list in topic_marks.items():
                if not marks_list:
                    continue
                
                # Sort by marks in descending order (highest first)
                sorted_marks = sorted(marks_list, key=lambda x: x[1], reverse=True)
                
                # Calculate ranks with ties
                ranks = {}
                current_rank = 1
                
                for i, (roll_no, marks) in enumerate(sorted_marks):
                    if i > 0 and marks < sorted_marks[i-1][1]:
                        # Different marks, update rank
                        current_rank = i + 1
                    ranks[roll_no] = current_rank
                
                topic_ranks[topic_name] = ranks
            
            return topic_ranks
            
        except Exception as e:
            print(f"Error calculating subject topic ranks for {subject_name}: {e}")
            return {}
    
    def get_student_report(self, class_name, roll_number):
        """Get detailed report for a specific student in a class"""
        try:
            data = self.get_sheet_data_for_class(class_name)
            
            if len(data) < 4:
                print(f"⚠️  Insufficient data for generating report")
                return None
            
            # All classes now use multi-subject layout for consistency
            return self.get_multi_subject_report(data, class_name, roll_number)
                
        except Exception as e:
            print(f"Error generating student report: {e}")
            return None
    
    def get_multi_subject_report(self, data, class_name, roll_number):
        """Handle multi-subject report for all classes - creates tabs for better organization"""
        try:
            subjects = {}
            
            print(f"🔍 Parsing multi-subject data for student {roll_number} in class {class_name}")
            
            # Parse subjects from the data by detecting the pattern
            # Find subject sections by detecting "Class" headers
            subject_sections = []
            for i, row in enumerate(data):
                if len(row) > 0 and str(row[0]).strip() == 'Class':
                    subject_sections.append(i)
            
            print(f"📊 Found {len(subject_sections)} subject sections: {subject_sections}")
            
            # Assign subjects based on position
            if len(subject_sections) >= 2:
                subjects['Maths'] = {'start_row': subject_sections[0]}
                subjects['Science'] = {'start_row': subject_sections[1]}
                print(f"✅ Assigned Maths to row {subject_sections[0]}, Science to row {subject_sections[1]}")
            elif len(subject_sections) == 1:
                # Single subject sheet with Class header
                subjects['Subject'] = {'start_row': subject_sections[0]}
                print(f"✅ Assigned Subject to row {subject_sections[0]}")
            else:
                # No Class headers found - treat entire sheet as one subject
                subjects['Subject'] = {'start_row': 0}
                print(f"✅ No Class headers found - treating as single subject starting at row 0")
            
            print(f"📊 Found subjects: {list(subjects.keys())}")
            
            # Process each subject
            report = {
                'Class': class_name,
                'Roll Number': roll_number,
                'Name': '',
                'subjects': {}
            }
            
            for subject_name, subject_info in subjects.items():
                print(f"🔄 Processing {subject_name} section...")
                start_row = subject_info['start_row']
                
                # Find header row for this subject
                header_row_idx = None
                for i in range(start_row, min(start_row + 5, len(data))):
                    if i < len(data) and len(data[i]) > 0 and 'Roll No.' in str(data[i][0]):
                        header_row_idx = i
                        break
                
                if header_row_idx is None:
                    print(f"⚠️  No header row found for {subject_name}")
                    continue
                
                headers = data[header_row_idx]
                data_start_row = header_row_idx + 2
                
                # Find the student row for this subject
                student_row = None
                for row_idx in range(data_start_row, len(data)):
                    if row_idx < len(data) and len(data[row_idx]) > 0:
                        # Stop if we hit another subject
                        if str(data[row_idx][0]).strip() and str(data[row_idx][0]).strip() == 'Class':
                            break
                        if str(data[row_idx][0]).strip() == str(roll_number):
                            student_row = data[row_idx]
                            if not report['Name'] and len(student_row) > 1:
                                report['Name'] = student_row[1]
                            break
                
                if student_row is None:
                    print(f"⚠️  Student {roll_number} not found in {subject_name} section")
                    continue
                
                # Get topic ranks for this subject
                subject_topic_ranks = self.calculate_subject_topic_ranks(data, subject_name, start_row)
                
                # Process topics for this subject
                subject_topics = []
                i = 2
                while i < len(headers):
                    topic_header = headers[i].strip() if i < len(headers) else ''
                    
                    if topic_header and topic_header.startswith('Topic'):
                        time_val = str(student_row[i]).strip() if i < len(student_row) and student_row[i] else ''
                        marks_val = str(student_row[i + 1]).strip() if i + 1 < len(student_row) and student_row[i + 1] else '0'
                        
                        # Only include topics that have actual marks data (not empty, not zero, and numeric)
                        if (marks_val and marks_val != '0' and marks_val != '' and marks_val.replace('.','').isdigit()):
                            marks = float(marks_val)
                            
                            # Get rank for this topic
                            rank = subject_topic_ranks.get(topic_header, {}).get(str(roll_number), 'N/A')
                            
                            # Calculate score percentage (assuming marks out of 12)
                            score_percentage = (marks / 12) * 100
                            
                            # Determine time category
                            time_category = 'below_avg' if 'below' in time_val.lower() else 'above_avg' if 'above' in time_val.lower() else 'unknown'
                            
                            # New performance categorization logic:
                            # Strong: below average time AND marks > 75% (9/12)
                            # Need Attention: above average time AND marks > 75% 
                            # Weak: marks <= 75% (regardless of time)
                            if score_percentage > 75:  # marks > 9/12
                                if time_category == 'below_avg':
                                    color = 'green'  # Strong - efficient learner
                                    performance_text = 'Strong'
                                    performance_class = 'bg-success'
                                else:
                                    color = 'orange'  # Need attention - good score but slow
                                    performance_text = 'Need Attention'
                                    performance_class = 'bg-warning text-dark'
                            else:
                                color = 'red'  # Weak - low score
                                performance_text = 'Weak'
                                performance_class = 'bg-danger'
                            
                            subject_topics.append({
                                'name': topic_header,
                                'time_category': time_val if time_val else 'Not Available',
                                'marks': marks,
                                'score_percentage': score_percentage,
                                'color': color,
                                'performance_class': performance_class,
                                'performance_text': performance_text,
                                'rank': rank
                            })
                        
                        i += 2
                    else:
                        i += 1
                
                print(f"✅ Found {len(subject_topics)} topics for {subject_name}")
                
                report['subjects'][subject_name] = {
                    'topics': subject_topics,
                    'total_topics': len(subject_topics),
                    'excellent_topics': len([t for t in subject_topics if t['marks'] >= 7.5]),
                    'growth_topics': len([t for t in subject_topics if t['marks'] < 7.5])
                }
            
            # Add overall performance analysis for multi-subject report
            all_topics = []
            for subject_data in report['subjects'].values():
                all_topics.extend(subject_data['topics'])
            
            # Count performance categories
            strong_count = len([t for t in all_topics if t['color'] == 'green'])
            need_attention_count = len([t for t in all_topics if t['color'] == 'orange'])
            weak_count = len([t for t in all_topics if t['color'] == 'red'])
            
            # Determine overall performance message and color
            if strong_count > need_attention_count and strong_count > weak_count:
                overall_performance = 'Good Going'
                overall_color = 'green'
            elif need_attention_count > strong_count and need_attention_count > weak_count:
                overall_performance = 'Need Attention'
                overall_color = 'yellow'
            elif weak_count > 0:
                overall_performance = 'Need Immediate Attention'
                overall_color = 'red'
            else:
                overall_performance = 'Good Going'
                overall_color = 'green'
            
            # Add analysis to report
            report['performance_analysis'] = {
                'strong_count': strong_count,
                'need_attention_count': need_attention_count,
                'weak_count': weak_count,
                'overall_performance': overall_performance,
                'overall_color': overall_color,
                'strong_topics': [t for t in all_topics if t['color'] == 'green'],
                'need_attention_topics': [t for t in all_topics if t['color'] == 'orange'],
                'weak_topics': [t for t in all_topics if t['color'] == 'red']
            }
            
            print(f"📊 Generated multi-subject report for {report['Name']} with {len(report['subjects'])} subjects")
            return report
            
        except Exception as e:
            print(f"Error generating multi-subject report: {e}")
            return None
    
    def get_single_subject_report(self, data, class_name, roll_number):
        """Handle single subject report (existing functionality)"""
        try:
            # Find header and data rows
            header_row_idx = 1
            for i, row in enumerate(data[:4]):
                if len(row) > 0 and 'Roll No.' in str(row[0]):
                    header_row_idx = i
                    break
            
            headers = data[header_row_idx]
            data_start_row = header_row_idx + 2
            
            # Find the student row
            for row in data[data_start_row:]:
                if len(row) > 0 and str(row[0]).strip() == str(roll_number):
                    
                    report = {
                        'Class': class_name,
                        'Roll Number': roll_number,
                        'Name': row[1] if len(row) > 1 else '',
                        'topics': []
                    }
                    
                    # Get topic ranks for the entire class
                    topic_ranks = self.calculate_topic_ranks(class_name)
                    
                    # Process topics starting from column 2
                    i = 2
                    while i < len(headers):
                        topic_header = headers[i].strip() if i < len(headers) else ''
                        
                        if topic_header and topic_header.startswith('Topic'):
                            topic_name = topic_header
                            time_val = str(row[i]).strip() if i < len(row) and row[i] else '0'
                            marks_val = str(row[i + 1]).strip() if i + 1 < len(row) and row[i + 1] else '0'
                            
                            # Only add topic if it has actual marks data (not empty, not zero, and numeric)
                            if (marks_val and marks_val != '0' and marks_val != '' and marks_val.replace('.','').isdigit()):
                                
                                # Get rank for this topic
                                rank = topic_ranks.get(topic_name, {}).get(str(roll_number), 'N/A')
                                
                                report['topics'].append({
                                    'name': topic_name,
                                    'time': time_val,
                                    'marks': marks_val,
                                    'rank': rank
                                })
                            
                            i += 2
                        else:
                            i += 1
                    
                    # Process topics for performance categorization
                    if report['topics']:
                        # Add performance categorization to each topic
                        for topic in report['topics']:
                            try:
                                # Handle marks - should be numeric
                                marks_num = float(topic['marks']) if topic['marks'] and topic['marks'].replace('.','').isdigit() else 0
                                score_percentage = (marks_num / 12) * 100
                                
                                # Handle time - could be text category or numeric
                                time_val = topic['time'].strip()
                                if 'above' in time_val.lower():
                                    time_category = 'above_avg'
                                elif 'below' in time_val.lower():
                                    time_category = 'below_avg'
                                else:
                                    # If it's numeric, we'll treat it as actual time (legacy support)
                                    try:
                                        time_num = float(time_val)
                                        # For numeric values, we can't determine above/below without context
                                        # So we'll default to below_avg for smaller numbers, above_avg for larger
                                        time_category = 'below_avg' if time_num <= 60 else 'above_avg'  # 60 minutes as arbitrary threshold
                                    except:
                                        time_category = 'below_avg'  # Default fallback
                                
                                # New performance categorization logic:
                                # Strong: below average time AND marks > 75% (9/12)
                                # Need Attention: above average time AND marks > 75% 
                                # Weak: marks <= 75% (regardless of time)
                                if score_percentage > 75:  # marks > 9/12
                                    if time_category == 'below_avg':
                                        color = 'green'  # Strong - efficient learner
                                        performance_text = 'Strong'
                                    else:
                                        color = 'orange'  # Need attention - good score but slow
                                        performance_text = 'Need Attention'
                                else:
                                    color = 'red'  # Weak - low score
                                    performance_text = 'Weak'
                                
                                # Add categorization info to topic
                                topic['score_percentage'] = score_percentage
                                topic['time_category'] = time_category
                                topic['color'] = color
                                topic['performance_text'] = 'Efficient' if color == 'green' else 'Good' if color == 'orange' else 'Needs Focus'
                                
                            except Exception as e:
                                print(f"Error processing topic {topic.get('name', 'Unknown')}: {e}")
                                # Set defaults
                                topic['score_percentage'] = 0
                                topic['time_category'] = 'below_avg'
                                topic['color'] = 'red'
                                topic['performance_text'] = 'Needs Focus'
                    
                    # Calculate summary statistics
                    excellent_topics = [t for t in report['topics'] if t.get('color') == 'green']
                    growth_topics = [t for t in report['topics'] if t.get('color') in ['orange', 'red']]
                    
                    report['total_topics'] = len(report['topics'])
                    report['excellent_topics'] = len(excellent_topics)
                    report['growth_topics'] = len(growth_topics)
                    report['excellent_topic_names'] = [t['name'] for t in excellent_topics]
                    report['growth_topic_names'] = [t['name'] for t in growth_topics]
                    
                    return report
            
            return None
            
        except Exception as e:
            print(f"Error generating single subject report: {e}")
            return None

# Initialize the connector
sheets_connector = GoogleSheetsConnector()

# Add all class sheet URLs (converted from pubhtml to CSV format)
sheets_connector.add_class_sheet_url('1B', 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTaKQHoSE52Y10HCKgwygRq_-qrr4WnfKK2i8we4mPULUH-Kjf0iRL_3iceAGhMR5issbBJLJtDPWoF/pub?output=csv')
sheets_connector.add_class_sheet_url('1C', 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTfkeAV8g62nZCsKI_fZ2aG0hHPaYaTnPd_YSXX1jk1K0Xx_8uvYyuOEGKibmtldj5H3D1It5JbZpHq/pub?output=csv')
sheets_connector.add_class_sheet_url('2A', 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQkRPm_zqNAvqIdS6-Wd1SoS5Tmka7L5wZzQZoDEzFEJ_wXsjQRPeihEwbBXtz8GYzT6dJ626tMtK4V/pub?output=csv')
sheets_connector.add_class_sheet_url('2B', 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSXU5WrP9nzibanbfjsjOoMpUdhQhxgynNLOuqzIUuw9VOo6QMnFYzaFY1jkjVP_JgZJtWZ3v5wsRNY/pub?output=csv')
sheets_connector.add_class_sheet_url('3A', 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQP0diP0IhdQZSirT1oZutI25UMQHfa8XY4DTgBPupOUh7cLBOnFnAmLN6YzKXMHXvbcqxPptJemuxb/pub?output=csv')
sheets_connector.add_class_sheet_url('3B', 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQFOwOqtnZlmgac6jNlDFjSheuFzbdUMcgIW32IiPyxDOdUalUe9eL3NuN3qR72xPztaQXDQz3x4TqK/pub?output=csv')
sheets_connector.add_class_sheet_url('4A', 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQ7d75CWqTm93BH_4pj9KdWterqOG4cixwzHr0POggL3yDwSwgfxjfrPhCQKY06Bg62tQc-V7-Ny607/pub?output=csv')
sheets_connector.add_class_sheet_url('5A', 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQzwxDvgMvk-0uGiharp6fRV0J6rg0Nnf1d5u_ND3kdcPskxNz_0iemf-bO87nyfiemZHf0QMbwZ-3-/pub?output=csv')
sheets_connector.add_class_sheet_url('6A', 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTNwiuUq48nzDvaxyeg5Cqa_rYE_coZ5pz4ss03ALj8SAy6mnVQxAp1wFfeAYSPPTXTydps3X-qhJXw/pub?output=csv')
sheets_connector.add_class_sheet_url('7A', 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRgyXOQGIHl4-86bCncg55yjNheiuiE6d6VFF5psYvyGdCovPnxT4A6d4Qo1NjawUHJfAQctkUig2GO/pub?output=csv')
sheets_connector.add_class_sheet_url('7B', 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTWXk09C63Cdt9Dk2v_UjusqVeesO6_-3GJmFlOgOj8YGHc8_qZghiI66XHRNu3WJfDz-578pmhGNRJ/pub?output=csv')
sheets_connector.add_class_sheet_url('8A', 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRs6QnT5Us9BTFdmDW4dXCZ2DXN487tWXfyAuVtuBZXOADm-7wNt139LcNHfpznHenwfLUsPLiKi4Yv/pub?output=csv')

@app.route('/')
def index():
    """Main page with class and student selection"""
    try:
        classes = sheets_connector.get_classes()
        return render_template('index.html', classes=classes)
    except Exception as e:
        print(f"Error loading classes for index page: {e}")
        return render_template('index.html', classes=[])

@app.route('/api/classes')
def get_classes_api():
    """API endpoint to get available classes"""
    try:
        classes = sheets_connector.get_classes()
        return jsonify({
            'success': True,
            'classes': classes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/students/<class_name>')
def get_students_api(class_name):
    """API endpoint to get students in a class"""
    try:
        students = sheets_connector.get_students_by_class(class_name)
        return jsonify({
            'success': True,
            'students': students
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/report/<class_name>/<roll_number>')
def student_report(class_name, roll_number):
    """Display student report page"""
    try:
        student_data = sheets_connector.get_student_report(class_name, roll_number)
        
        if not student_data:
            return render_template('error.html', 
                                 message=f"No data found for Roll Number {roll_number} in Class {class_name}")
        
        # Get current datetime for report generation timestamp
        current_time = datetime.now()
        
        return render_template('topic_report.html', student=student_data, report_time=current_time)
        
    except Exception as e:
        return render_template('error.html', message=f"Error: {str(e)}")

@app.route('/api/student-report/<class_name>/<roll_number>')
def get_student_report_api(class_name, roll_number):
    """API endpoint to get student report data"""
    try:
        student_data = sheets_connector.get_student_report(class_name, roll_number)
        return jsonify({
            'success': True,
            'student': student_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("🚀 Starting Student Report Application...")
    print("📋 Ready to accept individual sheet URLs for each class")
    print("💡 Use sheets_connector.add_class_sheet_url('1B', 'your_url_here') to add sheets")
    
    # For Render.com deployment, use the PORT environment variable
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
else:
    # Production configuration for WSGI servers
    application = app