"""
Django management command to create demo data for EduPulse app.
Run with: python manage.py create_demo_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from quizzes.models import Quiz, Question, Choice, Category
from core.models import UserProfile
import random


class Command(BaseCommand):
    help = 'Create demo data for EduPulse app'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo data for EduPulse...')
        
        # Create categories
        categories = self.create_categories()
        
        # Create demo users
        users = self.create_demo_users()
        
        # Create quizzes
        quizzes = self.create_quizzes(categories)
        
        # Create questions and choices for each quiz
        for quiz in quizzes:
            self.create_questions_for_quiz(quiz)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created demo data:\n'
                f'- {len(categories)} categories\n'
                f'- {len(users)} demo users\n'
                f'- {len(quizzes)} quizzes with questions'
            )
        )

    def create_categories(self):
        """Create quiz categories."""
        categories_data = [
            {'name': 'Mathematics', 'description': 'Math quizzes covering various topics'},
            {'name': 'Science', 'description': 'Science quizzes including physics, chemistry, and biology'},
            {'name': 'Programming', 'description': 'Coding and software development quizzes'},
            {'name': 'History', 'description': 'Historical events and figures'},
            {'name': 'Literature', 'description': 'Books, authors, and literary analysis'},
            {'name': 'Geography', 'description': 'World geography and countries'},
            {'name': 'Business', 'description': 'Business concepts and entrepreneurship'},
            {'name': 'Technology', 'description': 'Modern technology and digital trends'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        return categories

    def create_demo_users(self):
        """Create demo users with different roles."""
        users_data = [
            {
                'username': 'demo_student1',
                'email': 'student1@demo.com',
                'password': 'demo123',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'role': 'student'
            },
            {
                'username': 'demo_student2',
                'email': 'student2@demo.com',
                'password': 'demo123',
                'first_name': 'Bob',
                'last_name': 'Smith',
                'role': 'student'
            },
            {
                'username': 'demo_teacher1',
                'email': 'teacher1@demo.com',
                'password': 'demo123',
                'first_name': 'Dr. Sarah',
                'last_name': 'Wilson',
                'role': 'teacher'
            },
            {
                'username': 'demo_teacher2',
                'email': 'teacher2@demo.com',
                'password': 'demo123',
                'first_name': 'Prof. Michael',
                'last_name': 'Brown',
                'role': 'teacher'
            },
            {
                'username': 'demo_admin',
                'email': 'admin@demo.com',
                'password': 'demo123',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin'
            }
        ]
        
        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_staff': user_data['role'] == 'admin'
                }
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                
                # Create user profile
                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'role': user_data['role']}
                )
                
                self.stdout.write(f'Created user: {user.username} ({user_data["role"]})')
            else:
                profile = UserProfile.objects.get(user=user)
            
            users.append(user)
        
        return users

    def create_quizzes(self, categories):
        """Create demo quizzes."""
        # Get a teacher user to be the creator
        teacher_user = User.objects.filter(username='demo_teacher1').first()
        if not teacher_user:
            # Fallback to any user if teacher doesn't exist
            teacher_user = User.objects.first()
        
        quizzes_data = [
            {
                'title': 'Python Programming Basics',
                'description': 'Test your knowledge of Python fundamentals including variables, loops, and functions.',
                'difficulty': 'easy',
                'time_limit': 15,
                'passing_score': 70,
                'category': 'Programming',
                'is_active': True
            },
            {
                'title': 'Algebra Fundamentals',
                'description': 'Basic algebraic concepts including equations, inequalities, and functions.',
                'difficulty': 'easy',
                'time_limit': 20,
                'passing_score': 75,
                'category': 'Mathematics',
                'is_active': True
            },
            {
                'title': 'World History: Ancient Civilizations',
                'description': 'Explore the ancient civilizations of Egypt, Greece, Rome, and Mesopotamia.',
                'difficulty': 'medium',
                'time_limit': 25,
                'passing_score': 70,
                'category': 'History',
                'is_active': True
            },
            {
                'title': 'Chemistry: Atomic Structure',
                'description': 'Understanding atoms, elements, and the periodic table.',
                'difficulty': 'medium',
                'time_limit': 18,
                'passing_score': 80,
                'category': 'Science',
                'is_active': True
            },
            {
                'title': 'Digital Marketing Essentials',
                'description': 'Modern digital marketing strategies, SEO, and social media marketing.',
                'difficulty': 'medium',
                'time_limit': 30,
                'passing_score': 70,
                'category': 'Business',
                'is_active': True
            },
            {
                'title': 'JavaScript Fundamentals',
                'description': 'Core JavaScript concepts including variables, functions, and DOM manipulation.',
                'difficulty': 'easy',
                'time_limit': 20,
                'passing_score': 75,
                'category': 'Programming',
                'is_active': True
            },
            {
                'title': 'World Geography: Countries & Capitals',
                'description': 'Test your knowledge of world countries, their capitals, and major landmarks.',
                'difficulty': 'easy',
                'time_limit': 15,
                'passing_score': 70,
                'category': 'Geography',
                'is_active': True
            },
            {
                'title': 'Shakespeare\'s Works',
                'description': 'Famous plays, characters, and quotes from William Shakespeare.',
                'difficulty': 'medium',
                'time_limit': 25,
                'passing_score': 75,
                'category': 'Literature',
                'is_active': True
            }
        ]
        
        quizzes = []
        for quiz_data in quizzes_data:
            category = next(cat for cat in categories if cat.name == quiz_data['category'])
            
            quiz, created = Quiz.objects.get_or_create(
                title=quiz_data['title'],
                defaults={
                    'description': quiz_data['description'],
                    'difficulty': quiz_data['difficulty'],
                    'time_limit': quiz_data['time_limit'],
                    'passing_score': quiz_data['passing_score'],
                    'is_active': quiz_data['is_active'],
                    'created_by': teacher_user
                }
            )
            
            if created:
                quiz.categories.add(category)
                self.stdout.write(f'Created quiz: {quiz.title}')
            
            quizzes.append(quiz)
        
        return quizzes

    def create_questions_for_quiz(self, quiz):
        """Create questions and choices for a specific quiz."""
        if quiz.title == 'Python Programming Basics':
            self.create_python_questions(quiz)
        elif quiz.title == 'Algebra Fundamentals':
            self.create_algebra_questions(quiz)
        elif quiz.title == 'World History: Ancient Civilizations':
            self.create_history_questions(quiz)
        elif quiz.title == 'Chemistry: Atomic Structure':
            self.create_chemistry_questions(quiz)
        elif quiz.title == 'Digital Marketing Essentials':
            self.create_marketing_questions(quiz)
        elif quiz.title == 'JavaScript Fundamentals':
            self.create_javascript_questions(quiz)
        elif quiz.title == 'World Geography: Countries & Capitals':
            self.create_geography_questions(quiz)
        elif quiz.title == 'Shakespeare\'s Works':
            self.create_shakespeare_questions(quiz)

    def create_python_questions(self, quiz):
        """Create Python programming questions."""
        questions_data = [
            {
                'text': 'What is the correct way to create a variable in Python?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('x = 5', True),
                    ('var x = 5', False),
                    ('let x = 5', False),
                    ('const x = 5', False)
                ]
            },
            {
                'text': 'Which of the following is a valid Python data type?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('list', True),
                    ('array', False),
                    ('vector', False),
                    ('tuple', True)
                ]
            },
            {
                'text': 'What is the output of print(2 ** 3)?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('6', False),
                    ('8', True),
                    ('5', False),
                    ('Error', False)
                ]
            },
            {
                'text': 'How do you start a comment in Python?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('//', False),
                    ('#', True),
                    ('/*', False),
                    ('<!--', False)
                ]
            },
            {
                'text': 'What method is used to add an element to a list?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('add()', False),
                    ('append()', True),
                    ('insert()', True),
                    ('push()', False)
                ]
            }
        ]
        
        self.create_questions_from_data(quiz, questions_data)

    def create_algebra_questions(self, quiz):
        """Create algebra questions."""
        questions_data = [
            {
                'text': 'Solve for x: 2x + 5 = 13',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('x = 4', True),
                    ('x = 6', False),
                    ('x = 8', False),
                    ('x = 3', False)
                ]
            },
            {
                'text': 'What is the slope of the line y = 3x + 2?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('2', False),
                    ('3', True),
                    ('5', False),
                    ('1', False)
                ]
            },
            {
                'text': 'Factor the expression: x² - 4',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('(x + 2)(x - 2)', True),
                    ('(x + 4)(x - 4)', False),
                    ('(x + 1)(x - 4)', False),
                    ('Cannot be factored', False)
                ]
            },
            {
                'text': 'What is the solution to the inequality 3x - 6 > 0?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('x > 2', True),
                    ('x < 2', False),
                    ('x > 6', False),
                    ('x < 6', False)
                ]
            },
            {
                'text': 'What is the y-intercept of the line 2x + 3y = 6?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('2', True),
                    ('3', False),
                    ('6', False),
                    ('0', False)
                ]
            }
        ]
        
        self.create_questions_from_data(quiz, questions_data)

    def create_history_questions(self, quiz):
        """Create history questions."""
        questions_data = [
            {
                'text': 'Which ancient civilization built the pyramids?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Egyptians', True),
                    ('Greeks', False),
                    ('Romans', False),
                    ('Mesopotamians', False)
                ]
            },
            {
                'text': 'Who was the first emperor of Rome?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Julius Caesar', False),
                    ('Augustus', True),
                    ('Nero', False),
                    ('Constantine', False)
                ]
            },
            {
                'text': 'Which Greek philosopher was the teacher of Alexander the Great?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Socrates', False),
                    ('Plato', False),
                    ('Aristotle', True),
                    ('Pythagoras', False)
                ]
            },
            {
                'text': 'What was the capital of the Byzantine Empire?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Rome', False),
                    ('Athens', False),
                    ('Constantinople', True),
                    ('Alexandria', False)
                ]
            },
            {
                'text': 'Which ancient civilization developed the first writing system?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Egyptians', False),
                    ('Sumerians', True),
                    ('Greeks', False),
                    ('Chinese', False)
                ]
            }
        ]
        
        self.create_questions_from_data(quiz, questions_data)

    def create_chemistry_questions(self, quiz):
        """Create chemistry questions."""
        questions_data = [
            {
                'text': 'What is the atomic number of carbon?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('6', True),
                    ('12', False),
                    ('14', False),
                    ('8', False)
                ]
            },
            {
                'text': 'Which element has the chemical symbol "O"?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Oxygen', True),
                    ('Osmium', False),
                    ('Oganesson', False),
                    ('Osmium', False)
                ]
            },
            {
                'text': 'What is the charge of an electron?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Positive', False),
                    ('Negative', True),
                    ('Neutral', False),
                    ('Variable', False)
                ]
            },
            {
                'text': 'How many protons does a hydrogen atom have?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('0', False),
                    ('1', True),
                    ('2', False),
                    ('3', False)
                ]
            },
            {
                'text': 'What is the most abundant element in the universe?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Helium', False),
                    ('Carbon', False),
                    ('Hydrogen', True),
                    ('Oxygen', False)
                ]
            }
        ]
        
        self.create_questions_from_data(quiz, questions_data)

    def create_marketing_questions(self, quiz):
        """Create digital marketing questions."""
        questions_data = [
            {
                'text': 'What does SEO stand for?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Search Engine Optimization', True),
                    ('Social Engine Optimization', False),
                    ('Search Engine Organization', False),
                    ('Social Engine Organization', False)
                ]
            },
            {
                'text': 'Which social media platform is best for B2B marketing?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Instagram', False),
                    ('LinkedIn', True),
                    ('TikTok', False),
                    ('Snapchat', False)
                ]
            },
            {
                'text': 'What is a conversion rate?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Percentage of visitors who take a desired action', True),
                    ('Number of website visitors', False),
                    ('Cost per click', False),
                    ('Return on investment', False)
                ]
            },
            {
                'text': 'Which email marketing metric measures open rates?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Click-through rate', False),
                    ('Open rate', True),
                    ('Bounce rate', False),
                    ('Conversion rate', False)
                ]
            },
            {
                'text': 'What is content marketing?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Creating valuable content to attract customers', True),
                    ('Selling products online', False),
                    ('Email marketing campaigns', False),
                    ('Social media advertising', False)
                ]
            }
        ]
        
        self.create_questions_from_data(quiz, questions_data)

    def create_javascript_questions(self, quiz):
        """Create JavaScript questions."""
        questions_data = [
            {
                'text': 'How do you declare a variable in JavaScript?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('var x = 5', True),
                    ('let x = 5', True),
                    ('const x = 5', True),
                    ('variable x = 5', False)
                ]
            },
            {
                'text': 'What is the result of 2 + "2" in JavaScript?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('4', False),
                    ('22', True),
                    ('Error', False),
                    ('NaN', False)
                ]
            },
            {
                'text': 'How do you add an event listener in JavaScript?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('addEventListener()', True),
                    ('onClick()', False),
                    ('attachEvent()', False),
                    ('bindEvent()', False)
                ]
            },
            {
                'text': 'What is the purpose of JSON.parse()?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Convert JSON string to object', True),
                    ('Convert object to JSON string', False),
                    ('Parse HTML', False),
                    ('Validate JSON', False)
                ]
            },
            {
                'text': 'What is a closure in JavaScript?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('A function with access to variables in its outer scope', True),
                    ('A way to close browser windows', False),
                    ('A method to end loops', False),
                    ('A type of variable', False)
                ]
            }
        ]
        
        self.create_questions_from_data(quiz, questions_data)

    def create_geography_questions(self, quiz):
        """Create geography questions."""
        questions_data = [
            {
                'text': 'What is the capital of Japan?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Tokyo', True),
                    ('Kyoto', False),
                    ('Osaka', False),
                    ('Yokohama', False)
                ]
            },
            {
                'text': 'Which is the largest continent by area?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Asia', True),
                    ('Africa', False),
                    ('North America', False),
                    ('Europe', False)
                ]
            },
            {
                'text': 'What is the capital of Brazil?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Rio de Janeiro', False),
                    ('São Paulo', False),
                    ('Brasília', True),
                    ('Salvador', False)
                ]
            },
            {
                'text': 'Which ocean is the largest?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Atlantic', False),
                    ('Indian', False),
                    ('Pacific', True),
                    ('Arctic', False)
                ]
            },
            {
                'text': 'What is the capital of Australia?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Sydney', False),
                    ('Melbourne', False),
                    ('Canberra', True),
                    ('Brisbane', False)
                ]
            }
        ]
        
        self.create_questions_from_data(quiz, questions_data)

    def create_shakespeare_questions(self, quiz):
        """Create Shakespeare questions."""
        questions_data = [
            {
                'text': 'Who wrote "Romeo and Juliet"?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('William Shakespeare', True),
                    ('Christopher Marlowe', False),
                    ('Ben Jonson', False),
                    ('John Webster', False)
                ]
            },
            {
                'text': 'What is the famous quote from Hamlet?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('"To be or not to be"', True),
                    ('"All the world\'s a stage"', False),
                    ('"Now is the winter of our discontent"', False),
                    ('"Friends, Romans, countrymen"', False)
                ]
            },
            {
                'text': 'Which play features the character Lady Macbeth?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Macbeth', True),
                    ('Hamlet', False),
                    ('King Lear', False),
                    ('Othello', False)
                ]
            },
            {
                'text': 'What type of play is "A Midsummer Night\'s Dream"?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Comedy', True),
                    ('Tragedy', False),
                    ('History', False),
                    ('Romance', False)
                ]
            },
            {
                'text': 'Who says "The course of true love never did run smooth"?',
                'question_type': 'multiple_choice',
                'points': 1,
                'is_required': True,
                'choices': [
                    ('Lysander', True),
                    ('Romeo', False),
                    ('Hamlet', False),
                    ('Othello', False)
                ]
            }
        ]
        
        self.create_questions_from_data(quiz, questions_data)

    def create_questions_from_data(self, quiz, questions_data):
        """Helper method to create questions and choices from data."""
        for i, q_data in enumerate(questions_data):
            question = Question.objects.create(
                quiz=quiz,
                question_text=q_data['text'],
                question_type=q_data['question_type'],
                points=q_data['points'],
                is_required=q_data['is_required'],
                order=i + 1
            )
            
            for j, (choice_text, is_correct) in enumerate(q_data['choices']):
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=is_correct,
                    order=j + 1
                )
            
            self.stdout.write(f'  Created question: {question.question_text[:50]}...') 