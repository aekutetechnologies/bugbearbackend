import os
import certifi

body = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Our Platform</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .header {
            background-color: yellow;
            color: black;
            padding: 10px 0;
            text-align: center;
        }
        .content {
            padding: 20px;
            line-height: 1.6;
        }
        .content h1 {
            color: #333333;
        }
        .content p {
            color: #666666;
        }
        .footer {
            text-align: center;
            padding: 20px;
            background-color: #f4f4f4;
            color: #888888;
            font-size: 12px;
        }
        .button {
            display: inline-block;
            padding: 10px 20px;
            margin: 20px 0;
            font-size: 16px;
            color: black;
            background-color: yellow;
            text-decoration: none;
            border-radius: 5px;
        }
        .button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to [Your Platform Name]!</h1>
        </div>
        <div class="content">
            <h1>Hi [Client's Name],</h1>
            <p>Thank you for signing up for [Your Platform Name]. We are excited to have you on board!</p>
            <p>Here are a few things you can do to get started:</p>
            <ul>
                <li>Explore our features</li>
                <li>Check out our tutorials</li>
                <li>Join our community forum</li>
            </ul>
            <p>If you have any questions, feel free to reach out to our support team at any time.</p>
            <p>To get started, click the button below:</p>
            <a href="[Your Platform URL]" class="button">Get Started</a>
            <p>We look forward to helping you achieve your goals with [Your Platform Name].</p>
            <p>Best regards,<br>[Your Name]<br>[Your Position]</p>
        </div>
        <div class="footer">
            <p>&copy; 2024 [Your Company Name]. All rights reserved.</p>
            <p>[Your Company Address]</p>
        </div>
    </div>
</body>
</html>"""


class Util:
    @staticmethod
    def send_email(data):
        os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
        try:
            # email = EmailMessage(
            #     subject="Welcome to Bugbear",
            #     body=body,
            #     from_email="mailtrap@demomailtrap.com",
            #     to=["smrutivssutmca@gmail.com"],
            # )
            # email.content_subtype = "html"
            # email.send()
            # import smtplib

            # sender = "Private Person <mailtrap@demomailtrap.com>"
            # receiver = "A Test User <aekutetechnologies@gmail.com>"

            # message = f"""\
            # Subject: Hi Mailtrap
            # To: {receiver}
            # From: {sender}

            # This is a test e-mail message."""

            # with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
            #     server.starttls()
            #     server.login("api", "2c2650bc67bded2a1989549c77504aac")
            #     server.sendmail(sender, receiver, message)
            import mailtrap as mt

            mail = mt.MailFromTemplate(
                sender=mt.Address(
                    email="mailtrap@demomailtrap.com", name="BugBear Team"
                ),
                to=[mt.Address(email="aekutetechnologies@gmail.com")],
                template_uuid="c93a61c9-faa0-489a-971f-7a3cee1015b6",
                template_variables={
                    "user_name": data["name"],
                    "next_step_link": "Test_Next_step_link",
                    "get_started_link": "Test_Get_started_link",
                    "onboarding_video_link": "Test_Onboarding_video_link",
                },
            )

            client = mt.MailtrapClient(token="")
            client.send(mail)
            return True
        except Exception as e:
            print(e)
            return False
