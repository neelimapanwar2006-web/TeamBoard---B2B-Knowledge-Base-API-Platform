from django.core.management.base import BaseCommand

from api.models import KBEntry


ENTRIES = [
    ("What is a REST API?", "A REST API exposes resources over HTTP using standard methods such as GET, POST, PUT, and DELETE.", "api"),
    ("What is JWT authentication?", "JWT is a token-based authentication mechanism commonly used to authenticate API clients.", "api"),
    ("What are HTTP status codes?", "HTTP status codes communicate the outcome of an HTTP request, such as 200 for success and 404 for not found.", "api"),
    ("What is select_related in Django?", "select_related performs a SQL JOIN and fetches related foreign-key or one-to-one objects efficiently.", "database"),
    ("What is transaction.atomic?", "transaction.atomic groups database operations into a transaction that commits together or rolls back on failure.", "database"),
    ("What are Q objects in Django ORM?", "Q objects allow complex query conditions such as OR and AND combinations.", "database"),
    ("What is PostgreSQL?", "PostgreSQL is an open-source relational database management system.", "database"),
    ("What is Docker?", "Docker packages applications and dependencies into portable containers.", "cloud"),
    ("What is horizontal scaling?", "Horizontal scaling adds more application instances to distribute workload.", "cloud"),
    ("What is Django REST Framework?", "DRF is a toolkit for building Web APIs with Django.", "framework"),
    ("What is a Django signal?", "A signal allows decoupled code to react to framework events such as a model being saved.", "framework"),
    ("What is middleware in Django?", "Middleware is a layer that processes requests and responses around Django views.", "framework"),
]


class Command(BaseCommand):
    help = "Seed the TeamBoard knowledge base with sample entries."

    def handle(self, *args, **options):
        created = 0
        for question, answer, category in ENTRIES:
            _, was_created = KBEntry.objects.get_or_create(
                question=question,
                defaults={
                    "answer": answer,
                    "category": category,
                },
            )
            created += int(was_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete. Created {created} KB entries."
            )
        )
