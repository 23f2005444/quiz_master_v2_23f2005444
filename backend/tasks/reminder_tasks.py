import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import shared_task
from controllers.models import User, Quiz, QuizAttempt, Subject, Chapter
from controllers.extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@shared_task
def send_daily_reminders():
    """
    Send daily reminders to users about new quizzes or reminders to revisit.
    This task runs every evening at the scheduled time.
    """
    try:
        logger.info("Starting daily reminders task...")
        
        # Get all active users
        active_users = User.query.all()
        logger.info(f"Found {len(active_users)} users")
        
        if not active_users:
            logger.info("No users found in database")
            return {
                'status': 'success',
                'message': 'No users found to send reminders to',
                'timestamp': datetime.now().isoformat()
            }
        
        # Today and yesterday dates for checking new quizzes
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Get new quizzes created in the last 24 hours
        new_quizzes = Quiz.query.filter(
            func.date(Quiz.created_at) >= yesterday,
            Quiz.is_active == True
        ).all()
        
        logger.info(f"Found {len(new_quizzes)} new quizzes")
        
        # Find available quizzes that are active and not yet expired
        available_quizzes = Quiz.query.filter(
            Quiz.is_active == True,
            Quiz.is_locked == False
        ).all()
        
        # Filter quizzes that are actually available
        available_quiz_list = []
        for quiz in available_quizzes:
            try:
                if quiz.is_available():
                    available_quiz_list.append(quiz)
            except Exception as e:
                logger.warning(f"Error checking quiz availability for quiz {quiz.id}: {e}")
                continue
        
        logger.info(f"Found {len(available_quiz_list)} available quizzes")
        
        reminder_count = 0
        for user in active_users:
            try:
                logger.info(f"Processing user: {user.email}")
                
                # Check if user has been inactive for more than 7 days
                last_attempt = QuizAttempt.query.filter_by(user_id=user.id).order_by(
                    QuizAttempt.created_at.desc()
                ).first()
                
                # Determine if we should send a reminder
                should_remind = False
                reminder_reason = None
                
                if new_quizzes:
                    should_remind = True
                    reminder_reason = f"{len(new_quizzes)} new quizzes available"
                elif available_quiz_list and (not last_attempt or last_attempt.created_at < datetime.now() - timedelta(days=7)):
                    should_remind = True
                    reminder_reason = "It's been a while since your last quiz"
                elif available_quiz_list:  # Send to all users if there are available quizzes
                    should_remind = True
                    reminder_reason = "Don't miss out on available quizzes"
                
                if should_remind:
                    logger.info(f"Sending reminder to {user.email}: {reminder_reason}")
                    
                    # Prepare email content
                    subject = "Quiz Master - Daily Reminder"
                    
                    # Create context for email template
                    context = {
                        'user_name': user.full_name,
                        'new_quizzes': new_quizzes,
                        'available_quizzes': available_quiz_list[:5],  # Limit to 5
                        'reminder_reason': reminder_reason,
                        'app_url': os.getenv('APP_URL', 'http://localhost:5173'),
                    }
                    
                    # Use simple HTML template for email
                    html_content = create_daily_reminder_html(context)
                    
                    # Send the email
                    success = send_email_safe(user.email, subject, html_content)
                    
                    if success:
                        reminder_count += 1
                        logger.info(f"✅ Daily reminder sent to {user.email}")
                    else:
                        logger.error(f"❌ Failed to send reminder to {user.email}")
                else:
                    logger.info(f"Skipping {user.email} - no reminders needed")
                        
            except Exception as user_error:
                logger.error(f"Error processing user {user.email}: {str(user_error)}")
                continue
        
        result = {
            'status': 'success',
            'message': f'Successfully sent {reminder_count} daily reminders out of {len(active_users)} users',
            'timestamp': datetime.now().isoformat()
        }
        logger.info(f"Task completed: {result}")
        return result
    
    except Exception as e:
        error_msg = f"Error sending daily reminders: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            'status': 'error',
            'message': error_msg,
            'timestamp': datetime.now().isoformat()
        }


@shared_task
def send_monthly_activity_report():
    """
    Generate and send monthly activity reports to all users.
    This task runs on the first day of every month.
    """
    try:
        logger.info("Starting monthly activity report task...")
        
        # Get all users
        users = User.query.all()
        logger.info(f"Found {len(users)} users")
        
        if not users:
            logger.info("No users found in database")
            return {
                'status': 'success',
                'message': 'No users found to send reports to',
                'timestamp': datetime.now().isoformat()
            }
        
        # Calculate previous month's date range
        today = datetime.now().date()
        first_day_this_month = today.replace(day=1)
        last_day_prev_month = first_day_this_month - timedelta(days=1)
        first_day_prev_month = last_day_prev_month.replace(day=1)
        
        month_name = last_day_prev_month.strftime("%B %Y")
        logger.info(f"Generating reports for: {month_name}")
        
        report_count = 0
        for user in users:
            try:
                logger.info(f"Processing user: {user.email}")
                
                # Get all attempts by the user in the previous month
                attempts = QuizAttempt.query.filter(
                    QuizAttempt.user_id == user.id,
                    QuizAttempt.created_at >= first_day_prev_month,
                    QuizAttempt.created_at <= last_day_prev_month
                ).all()
                
                # For testing purposes, if no previous month data, use current month or send anyway
                if not attempts:
                    # Try current month for testing
                    attempts = QuizAttempt.query.filter(
                        QuizAttempt.user_id == user.id,
                        QuizAttempt.created_at >= first_day_this_month
                    ).all()
                
                # If still no attempts, send a basic report anyway
                if not attempts:
                    logger.info(f"No activity found for {user.email}, sending basic report")
                    
                    # Create basic report for user with no activity
                    context = {
                        'user_name': user.full_name,
                        'month_name': month_name,
                        'total_attempts': 0,
                        'completed_attempts': 0,
                        'average_score': 0,
                        'passing_rate': 0,
                        'performance_level': 'No Activity',
                        'rank': 1,
                        'total_users': len(users),
                        'app_url': os.getenv('APP_URL', 'http://localhost:5173')
                    }
                else:
                    logger.info(f"Found {len(attempts)} attempts for {user.email}")
                    
                    # Calculate statistics
                    total_attempts = len(attempts)
                    completed_attempts = sum(1 for a in attempts if a.status == 'completed')
                    total_score = sum(a.score or 0 for a in attempts)
                    total_possible = sum(a.total_marks or 1 for a in attempts)
                    average_score = (total_score / total_possible) * 100 if total_possible > 0 else 0
                    passed_count = sum(1 for a in attempts if a.is_passed)
                    passing_rate = (passed_count / completed_attempts) * 100 if completed_attempts > 0 else 0
                    
                    # Performance level based on average score
                    performance_level = "Excellent" if average_score >= 90 else \
                                       "Good" if average_score >= 75 else \
                                       "Satisfactory" if average_score >= 60 else \
                                       "Needs Improvement"
                    
                    # Context for the email template
                    context = {
                        'user_name': user.full_name,
                        'month_name': month_name,
                        'total_attempts': total_attempts,
                        'completed_attempts': completed_attempts,
                        'average_score': round(average_score, 1),
                        'passing_rate': round(passing_rate, 1),
                        'performance_level': performance_level,
                        'rank': 1,  # Simplified for now
                        'total_users': len(users),
                        'app_url': os.getenv('APP_URL', 'http://localhost:5173')
                    }
                
                # Create email content
                subject = f"Quiz Master - Monthly Activity Report ({month_name})"
                
                # Use simple HTML template for email
                html_content = create_monthly_report_html(context)
                
                # Send the email
                success = send_email_safe(user.email, subject, html_content)
                
                if success:
                    report_count += 1
                    logger.info(f"✅ Monthly report sent to {user.email}")
                else:
                    logger.error(f"❌ Failed to send report to {user.email}")
                    
            except Exception as user_error:
                logger.error(f"Error processing user {user.email}: {str(user_error)}")
                continue
        
        result = {
            'status': 'success',
            'message': f'Successfully sent {report_count} monthly reports out of {len(users)} users',
            'timestamp': datetime.now().isoformat()
        }
        logger.info(f"Task completed: {result}")
        return result
    
    except Exception as e:
        error_msg = f"Error sending monthly reports: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            'status': 'error',
            'message': error_msg,
            'timestamp': datetime.now().isoformat()
        }


def send_email_safe(recipient, subject, html_content):
    """
    Safer email sending function with better error handling
    """
    try:
        logger.info(f"Attempting to send email to {recipient}")
        
        # Setup email server (MailHog) - NO USERNAME/PASSWORD NEEDED
        smtp_server = os.getenv('SMTP_SERVER', 'localhost')
        smtp_port = int(os.getenv('SMTP_PORT', 1025))  # MailHog default port
        sender_email = os.getenv('SENDER_EMAIL', 'noreply@quizmaster.com')
        
        logger.info(f"Using SMTP: {smtp_server}:{smtp_port}")
        
        # Create email message
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = f"Quiz Master <{sender_email}>"
        message['To'] = recipient
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)
        
        # Send email with better error handling
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                # Set timeout to avoid hanging
                server.timeout = 30
                
                # NO LOGIN NEEDED FOR MAILHOG!
                server.sendmail(sender_email, recipient, message.as_string())
                
            logger.info(f"✅ Email sent successfully to {recipient}")
            return True
            
        except smtplib.SMTPException as smtp_error:
            logger.error(f"SMTP error sending to {recipient}: {str(smtp_error)}")
            return False
        except ConnectionError as conn_error:
            logger.error(f"Connection error sending to {recipient}: {str(conn_error)}")
            return False
        except Exception as send_error:
            logger.error(f"Unexpected error sending to {recipient}: {str(send_error)}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Email setup error for {recipient}: {str(e)}")
        return False


def create_daily_reminder_html(context):
    """Create HTML for daily reminder email"""
    
    new_quizzes_html = ""
    if context['new_quizzes']:
        new_quizzes_html = f"""
            <h2 style="color: #4f46e5; font-size: 20px;">New Quizzes Available</h2>
            <p>We've added {len(context['new_quizzes'])} new quizzes since yesterday:</p>
        """
        
        for quiz in context['new_quizzes']:
            new_quizzes_html += f"""
                <div style="margin-bottom: 10px; padding: 10px; border-left: 3px solid #4f46e5; background-color: white;">
                    <div style="font-weight: bold; color: #4f46e5;">{quiz.title}</div>
                    <div>Chapter: {quiz.chapter.name}</div>
                    <div>Subject: {quiz.chapter.subject.name}</div>
                </div>
            """
    
    available_quizzes_html = ""
    for quiz in context['available_quizzes']:
        available_quizzes_html += f"""
            <div style="margin-bottom: 10px; padding: 10px; border-left: 3px solid #4f46e5; background-color: white;">
                <div style="font-weight: bold; color: #4f46e5;">{quiz.title}</div>
                <div>Chapter: {quiz.chapter.name}</div>
                <div>Subject: {quiz.chapter.subject.name}</div>
                <div>Duration: {quiz.time_duration} minutes</div>
            </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Quiz Master - Daily Reminder</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #4f46e5; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">Quiz Master</h1>
        </div>
        <div style="background-color: #f9fafb; padding: 20px; border-radius: 0 0 5px 5px; border: 1px solid #e5e7eb; border-top: none;">
            <p>Hello {context['user_name']},</p>
            
            <p>We noticed that <span style="font-weight: bold; color: #4f46e5;">{context['reminder_reason']}</span>. Here's a quick update:</p>
            
            {new_quizzes_html}
            
            <h2 style="color: #4f46e5; font-size: 20px;">Available Quizzes</h2>
            <p>Here are some quizzes you can take right now:</p>
            
            {available_quizzes_html}
            
            <p>Regular practice leads to better results. Don't miss out on improving your knowledge!</p>
            
            <div style="text-align: center;">
                <a href="{context['app_url']}" style="display: inline-block; background-color: #4f46e5; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; margin-top: 15px; font-weight: bold;">Start a Quiz Now</a>
            </div>
        </div>
        <div style="text-align: center; margin-top: 20px; font-size: 12px; color: #6b7280;">
            <p>This is an automated reminder from Quiz Master.</p>
            <p>© {datetime.now().year} Quiz Master. All rights reserved.</p>
        </div>
    </body>
    </html>
    """


def create_monthly_report_html(context):
    """Create HTML for monthly report email"""
    
    # Determine performance level class
    performance_class = ""
    if context['performance_level'] == 'Excellent':
        performance_class = "color: #047857;"
    elif context['performance_level'] == 'Good':
        performance_class = "color: #0369a1;"
    elif context['performance_level'] == 'Satisfactory':
        performance_class = "color: #b45309;"
    else:
        performance_class = "color: #b91c1c;"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Quiz Master - Monthly Activity Report</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 700px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #4f46e5; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">Monthly Activity Report</h1>
            <p>{context['month_name']}</p>
        </div>
        <div style="background-color: #f9fafb; padding: 20px; border-radius: 0 0 5px 5px; border: 1px solid #e5e7eb; border-top: none;">
            <p>Hello {context['user_name']},</p>
            
            <p>Here's your monthly activity report for <strong>{context['month_name']}</strong>.</p>
            
            <h2 style="color: #4f46e5; font-size: 20px;">Monthly Performance</h2>
            
            <div style="display: flex; flex-wrap: wrap; margin: 0 -10px;">
                <div style="flex: 1; min-width: 120px; margin: 10px; padding: 15px; background-color: white; border-radius: 5px; text-align: center;">
                    <div style="font-size: 14px; color: #6b7280;">Total Attempts</div>
                    <div style="font-size: 24px; font-weight: bold; color: #4f46e5; margin: 10px 0;">{context['total_attempts']}</div>
                </div>
                
                <div style="flex: 1; min-width: 120px; margin: 10px; padding: 15px; background-color: white; border-radius: 5px; text-align: center;">
                    <div style="font-size: 14px; color: #6b7280;">Completed</div>
                    <div style="font-size: 24px; font-weight: bold; color: #4f46e5; margin: 10px 0;">{context['completed_attempts']}</div>
                </div>
                
                <div style="flex: 1; min-width: 120px; margin: 10px; padding: 15px; background-color: white; border-radius: 5px; text-align: center;">
                    <div style="font-size: 14px; color: #6b7280;">Average Score</div>
                    <div style="font-size: 24px; font-weight: bold; color: #4f46e5; margin: 10px 0;">{context['average_score']}%</div>
                </div>
                
                <div style="flex: 1; min-width: 120px; margin: 10px; padding: 15px; background-color: white; border-radius: 5px; text-align: center;">
                    <div style="font-size: 14px; color: #6b7280;">Passing Rate</div>
                    <div style="font-size: 24px; font-weight: bold; color: #4f46e5; margin: 10px 0;">{context['passing_rate']}%</div>
                </div>
            </div>
            
            <h2 style="color: #4f46e5; font-size: 20px;">Your Standing</h2>
            
            <p>You are ranked <span style="display: inline-block; padding: 5px 10px; background-color: #4f46e5; color: white; border-radius: 15px; font-weight: bold;">#{context['rank']}</span> out of {context['total_users']} active users this month.</p>
            
            <p>Your performance level: 
                <strong style="{performance_class}">{context['performance_level']}</strong>
            </p>
            
            <p>Regular practice leads to better results. Keep up the good work!</p>
            
            <div style="text-align: center;">
                <a href="{context['app_url']}" style="display: inline-block; background-color: #4f46e5; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; margin-top: 15px; font-weight: bold;">View All Attempts</a>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 20px; font-size: 12px; color: #6b7280;">
            <p>This is an automated monthly report from Quiz Master.</p>
            <p>© {datetime.now().year} Quiz Master. All rights reserved.</p>
        </div>
    </body>
    </html>
    """