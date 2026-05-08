import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date


def send_reminder_email(to_email, user_name='用户', config=None):
    smtp_host = config['SMTP_HOST']
    smtp_port = config['SMTP_PORT']
    smtp_user = config['SMTP_USER']
    smtp_pass = config['SMTP_PASS']

    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header('别忘了今天的称重哦~', 'utf-8')
    form_name = Header("体重记录小助手", "utf-8").encode()
    msg['From'] = f'{form_name} <{smtp_user}>'
    msg['To'] = to_email

    html_content = f'''
    <div style="max-width:600px;margin:0 auto;padding:30px;background:linear-gradient(135deg,#fff5f5,#ffe8e8);border-radius:20px;font-family:'Microsoft YaHei','PingFang SC',sans-serif;">
        <div style="text-align:center;padding:20px;">
            <h1 style="color:#ff6b6b;font-size:24px;margin:0;">每日称重提醒</h1>
        </div>
        <div style="background:white;border-radius:15px;padding:30px;margin:20px 0;text-align:center;">
            <p style="font-size:18px;color:#555;line-height:1.8;">
                亲爱的 {user_name}，<br>
                今天还没有记录体重哦~<br>
                赶紧来记录一下吧！
            </p>
            <p style="font-size:14px;color:#999;margin-top:20px;">
                坚持每天记录，见证每一滴进步
            </p>
        </div>
        <div style="text-align:center;padding:10px;">
            <p style="font-size:12px;color:#ccc;">
                此邮件由系统自动发送，如需关闭提醒请在系统中设置
            </p>
        </div>
    </div>
    '''

    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [to_email], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f'发送邮件失败: {e}')
        return False


def check_and_send_reminders(app=None):
    if app:
        ctx = app.app_context()
        ctx.push()

    try:
        from models import User, UserReminderSetting, WeightRecord
        from app import db

        today = date.today()

        reminders = UserReminderSetting.query.filter_by(email_reminder_enabled=True).all()

        for reminder in reminders:
            today_record = WeightRecord.query.filter_by(
                user_id=reminder.user_id,
                record_date=today
            ).first()

            if not today_record:
                user = User.query.get(reminder.user_id)
                if user:
                    success = send_reminder_email(user.email, user.email.split('@')[0], config=app.config)
                    if success:
                        print(f'已发送提醒邮件至 {user.email}')
    except Exception as e:
        print(f'提醒任务执行失败: {e}')
    finally:
        if app:
            ctx.pop()
