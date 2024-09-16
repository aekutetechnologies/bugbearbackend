from django.core.management.base import BaseCommand
from jobs.models import BugJob, BugJobCategory
from buguser.models import BugOrganization
from django.utils import timezone
import random
from datetime import timedelta


class Command(BaseCommand):
    help = "Populate the database with a large number of test data using bulk_create"

    def handle(self, *args, **kwargs):
        # List of company names
        # List of company names
        company_names = [
            "Nokia",
            "Amazon",
            "Flipkart",
            "Google",
            "Microsoft",
            "Apple",
            "Facebook",
            "Twitter",
            "Netflix",
            "IBM",
            "Oracle",
            "Adobe",
            "Salesforce",
            "Intel",
            "Samsung",
            "Sony",
            "Dell",
            "HP",
            "Cisco",
            "Huawei",
            "Samsung",
            "LG",
            "Qualcomm",
            "SAP",
            "Tata Consultancy Services",
            "Infosys",
            "Wipro",
            "HCL Technologies",
            "Accenture",
            "Capgemini",
            "Cognizant",
            "AT&T",
            "Verizon",
            "Zoom",
            "Adobe",
            "Uber",
            "Lyft",
            "Airbnb",
            "Dropbox",
            "Slack",
            "Spotify",
            "Reddit",
            "Shopify",
            "Square",
            "Stripe",
            "Etsy",
            "Snapchat",
            "LinkedIn",
            "Salesforce",
            "ServiceNow",
            "Palantir",
            "Twilio",
            "Datadog",
            "Elastic",
            "Splunk",
            "MongoDB",
            "Redis",
            "Elastic",
            "Fujitsu",
            "Lenovo",
            "Xiaomi",
            "OnePlus",
            "Oppo",
            "Realme",
            "Asus",
            "Acer",
            "MSI",
            "Razer",
            "NVIDIA",
            "AMD",
            "Broadcom",
            "Texas Instruments",
            "Analog Devices",
            "National Instruments",
            "Microchip Technology",
            "Roche",
            "Pfizer",
            "Johnson & Johnson",
            "Merck",
            "Novartis",
            "GlaxoSmithKline",
            "Sanofi",
            "AstraZeneca",
            "Boeing",
            "Airbus",
            "Lockheed Martin",
            "Northrop Grumman",
            "Raytheon",
            "General Dynamics",
            "Thales",
            "Siemens",
            "Bosch",
            "Schneider Electric",
            "Honeywell",
            "ABB",
            "Rockwell Automation",
            "Emerson",
            "Eaton",
            "Parker Hannifin",
            "Stryker",
            "Medtronic",
            "Boston Scientific",
            "Zimmer Biomet",
            "Thermo Fisher Scientific",
            "PerkinElmer",
            "Becton Dickinson",
            "Illumina",
            "Agilent Technologies",
            "Danaher",
            "Waters Corporation",
            "Bruker",
            "Toshiba",
            "Hitachi",
            "NEC",
            "Panasonic",
            "Sharp",
            "Mitsubishi Electric",
            "Kyocera",
            "Ricoh",
            "Seiko Epson",
            "Canon",
            "Nikon",
            "Leica",
            "Hasselblad",
            "Olympus",
            "Pentax",
            "Fujifilm",
            "Kodak",
            "Phase One",
        ]

        # Create organizations
        organizations = [
            BugOrganization(
                org_name=name,
                org_email=f'contact_{name.lower().replace(" ", "_")}@example.com',
                org_password=f"securepassword_{i + 1}",
            )
            for i, name in enumerate(company_names)
        ]
        BugOrganization.objects.bulk_create(organizations)

        # Get all created organizations
        all_organizations = BugOrganization.objects.all()

        # Create categories
        categories = [
            BugJobCategory(name="DevSecOps"),
            BugJobCategory(name="Cloud Security"),
            BugJobCategory(name="Security Auditing"),
            BugJobCategory(name="Web Application Security"),
            BugJobCategory(name="Vulerability Management"),
            BugJobCategory(name="VPAT"),
            BugJobCategory(name="Network Security"),
            BugJobCategory(name="Physical Red Teaming"),
            BugJobCategory(name="Physical Security"),
            BugJobCategory(name="WebProxy"),
            BugJobCategory(name="EDR/XDR"),
            BugJobCategory(name="SOCaaS"),
            BugJobCategory(name="AD Security/AD Pentesting"),
        ]
        BugJobCategory.objects.bulk_create(categories)

        # Get all created categories
        all_categories = BugJobCategory.objects.all()

        # Define the start and end dates of the current year
        today = timezone.now().date()
        start_of_year = today.replace(month=1, day=1)
        end_of_year = today.replace(month=12, day=31)

        def random_date(start, end):
            """Generate a random date between start and end."""
            delta = end - start
            random_days = random.randint(0, delta.days)
            return start + timedelta(days=random_days)

        # List of specific job titles
        job_titles = [
            # Python Developer Titles
            "Junior Python Developer",
            "Senior Python Developer",
            "Python Developer",
            "Python Engineer",
            "Lead Python Developer",
            "Python Backend Developer",
            "Python Full Stack Developer",
            "Senior Python Backend Developer",
            "Junior Python Data Scientist",
            "Senior Python Data Scientist",
            "Python Web Developer",
            "Python Automation Engineer",
            # Django Developer Titles
            "Junior Django Developer",
            "Senior Django Developer",
            "Django Developer",
            "Django Backend Developer",
            "Django Full Stack Developer",
            "Lead Django Developer",
            "Junior Django Web Developer",
            "Senior Django Web Developer",
            # Frontend Developer Titles
            "Junior Frontend Developer",
            "Senior Frontend Developer",
            "Frontend Developer",
            "Frontend Engineer",
            "Lead Frontend Developer",
            "React Developer",
            "Angular Developer",
            "Vue.js Developer",
            "HTML/CSS Developer",
            # Full Stack Developer Titles
            "Junior Full Stack Developer",
            "Senior Full Stack Developer",
            "Full Stack Developer",
            "Lead Full Stack Developer",
            # Mobile Developer Titles
            "Junior Mobile Developer",
            "Senior Mobile Developer",
            "Mobile Developer",
            "iOS Developer",
            "Android Developer",
            "Flutter Developer",
            "React Native Developer",
            # DevOps and System Admin Titles
            "Junior DevOps Engineer",
            "Senior DevOps Engineer",
            "DevOps Engineer",
            "System Administrator",
            "Senior System Administrator",
            "DevOps Specialist",
            "Site Reliability Engineer",
            # Data Science and Analytics Titles
            "Junior Data Scientist",
            "Senior Data Scientist",
            "Data Scientist",
            "Data Analyst",
            "Junior Data Analyst",
            "Senior Data Analyst",
            "Machine Learning Engineer",
            "Data Engineer",
            "Business Intelligence Analyst",
            # QA and Testing Titles
            "Junior QA Engineer",
            "Senior QA Engineer",
            "QA Engineer",
            "Lead QA Engineer",
            "Test Automation Engineer",
            "Manual Tester",
            # Project Management Titles
            "Junior Project Manager",
            "Senior Project Manager",
            "Project Manager",
            "Scrum Master",
            "Agile Coach",
            # UX/UI Designer Titles
            "Junior UX Designer",
            "Senior UX Designer",
            "UX Designer",
            "UI Designer",
            "Lead UX Designer",
            "Lead UI Designer",
            # Support and IT Titles
            "Junior IT Support Specialist",
            "Senior IT Support Specialist",
            "IT Support Specialist",
            "Technical Support Engineer",
            "Help Desk Technician",
            # Miscellaneous Titles
            "Software Engineer",
            "Software Developer",
            "Application Developer",
            "Solutions Architect",
            "Technical Lead",
            "Technical Consultant",
            # Variations with technologies
            "JavaScript Developer",
            "TypeScript Developer",
            "Node.js Developer",
            "PHP Developer",
            "Ruby on Rails Developer",
            "C# Developer",
            "Java Developer",
            "Swift Developer",
            "Kotlin Developer",
            "Golang Developer",
            "C++ Developer",
            "C Developer",
            "Rust Developer",
        ] * 10  # Multiply to ensure you have a diverse set of job titles, adjust the multiplier as needed

        # Create 5000 jobs
        jobs = [
            BugJob(
                title=random.choice(job_titles),
                company=random.choice(all_organizations),
                category=random.choice(all_categories),
                job_description="Sample job description goes here.",
                responsibilities="Sample responsibilities go here.",
                job_posted=random_date(start_of_year, end_of_year),
                job_expiry=random_date(start_of_year, end_of_year) + timedelta(days=random.randint(30, 180)),
                salary_min=random.uniform(30000, 70000),
                salary_max=random.uniform(70000, 120000),
                location="Sample Location",
                job_type=random.choice(["Full Time", "Part Time", "Contract", "Internship"]),
                experience=random.uniform(0, 15),  # Experience in years as a float
                education=random.choice(["Graduation", "Master's Degree", "PhD"]),
                featured=random.choice([True, False]),
            )
            for i in range(5000)
        ]

        # Bulk create jobs
        BugJob.objects.bulk_create(jobs)

        self.stdout.write(self.style.SUCCESS("Successfully populated the database with test data."))
