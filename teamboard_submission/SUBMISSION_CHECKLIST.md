# Submission Checklist

## Local verification
- [ ] Copy `.env.example` to `.env`
- [ ] Set a strong `DJANGO_SECRET_KEY`
- [ ] Set PostgreSQL password
- [ ] Run `docker compose up --build`
- [ ] Run `docker compose exec web python manage.py seed_kb`
- [ ] Run `docker compose exec web python manage.py test`
- [ ] Import the Postman collection
- [ ] Register a client
- [ ] Login
- [ ] Test protected query
- [ ] Make a zero-result query
- [ ] Create an admin user and set Company.role to `admin`
- [ ] Test usage summary
- [ ] Verify `.env` is NOT tracked by Git

## GitHub
- [ ] Create a new GitHub repository
- [ ] Push the project
- [ ] Confirm README renders correctly
- [ ] Confirm `requirements.txt` is present
- [ ] Confirm `postman/TeamBoard.postman_collection.json` is present
- [ ] Submit the GitHub repository URL
