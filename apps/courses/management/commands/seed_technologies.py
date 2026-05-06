from django.core.management.base import BaseCommand
from apps.courses.models import Technology


class Command(BaseCommand):
    help = 'Seed technology data with categories and options'

    def handle(self, *args, **options):
        # Clear existing technologies
        Technology.objects.all().delete()
        
        # Technology data based on user's JSON structure
        technologies_data = [
            # Frontend technologies
            {
                'category': 'frontend',
                'label': 'React',
                'value': 'react',
                'description': 'A JavaScript library for building user interfaces'
            },
            {
                'category': 'frontend',
                'label': 'Vue',
                'value': 'vue',
                'description': 'The Progressive JavaScript Framework'
            },
            {
                'category': 'frontend',
                'label': 'Angular',
                'value': 'angular',
                'description': 'Platform for building mobile and desktop web applications'
            },
            {
                'category': 'frontend',
                'label': 'Next.js',
                'value': 'nextjs',
                'description': 'The React Framework for Production'
            },
            {
                'category': 'frontend',
                'label': 'Nuxt.js',
                'value': 'nuxtjs',
                'description': 'The Intuitive Vue Framework'
            },
            
            # Backend technologies
            {
                'category': 'backend',
                'label': 'Node.js',
                'value': 'node',
                'description': 'JavaScript runtime built on Chrome\'s V8 JavaScript engine'
            },
            {
                'category': 'backend',
                'label': 'Django',
                'value': 'django',
                'description': 'The web framework for perfectionists with deadlines'
            },
            {
                'category': 'backend',
                'label': 'Flask',
                'value': 'flask',
                'description': 'A lightweight WSGI web application framework'
            },
            {
                'category': 'backend',
                'label': 'FastAPI',
                'value': 'fastapi',
                'description': 'Modern, fast web framework for building APIs with Python'
            },
            {
                'category': 'backend',
                'label': 'Express.js',
                'value': 'express',
                'description': 'Fast, unopinionated, minimalist web framework for Node.js'
            },
            
            # Database technologies
            {
                'category': 'database',
                'label': 'PostgreSQL',
                'value': 'postgresql',
                'description': 'The World\'s Most Advanced Open Source Relational Database'
            },
            {
                'category': 'database',
                'label': 'MySQL',
                'value': 'mysql',
                'description': 'The World\'s Most Popular Open Source Database'
            },
            {
                'category': 'database',
                'label': 'MongoDB',
                'value': 'mongodb',
                'description': 'The most popular NoSQL database'
            },
            {
                'category': 'database',
                'label': 'Redis',
                'value': 'redis',
                'description': 'Open source, in-memory data structure store'
            },
            
            # DevOps technologies
            {
                'category': 'devops',
                'label': 'Docker',
                'value': 'docker',
                'description': 'Platform for developing, shipping, and running applications'
            },
            {
                'category': 'devops',
                'label': 'Kubernetes',
                'value': 'kubernetes',
                'description': 'Production-Grade Container Scheduling and Management'
            },
            {
                'category': 'devops',
                'label': 'AWS',
                'value': 'aws',
                'description': 'Amazon Web Services - Cloud Computing Services'
            },
            {
                'category': 'devops',
                'label': 'CI/CD',
                'value': 'cicd',
                'description': 'Continuous Integration and Continuous Deployment'
            },
            
            # Mobile technologies
            {
                'category': 'mobile',
                'label': 'React Native',
                'value': 'react-native',
                'description': 'Build mobile apps using React'
            },
            {
                'category': 'mobile',
                'label': 'Flutter',
                'value': 'flutter',
                'description': 'Google\'s UI toolkit for building natively compiled applications'
            },
            {
                'category': 'mobile',
                'label': 'Swift',
                'value': 'swift',
                'description': 'Powerful and intuitive programming language for iOS'
            },
            {
                'category': 'mobile',
                'label': 'Kotlin',
                'value': 'kotlin',
                'description': 'Modern programming language for Android development'
            }
        ]
        
        # Create technologies
        created_count = 0
        for tech_data in technologies_data:
            technology = Technology.objects.create(**tech_data)
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created technology: {technology.get_category_display()} - {technology.label}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully seeded {created_count} technologies!')
        )
