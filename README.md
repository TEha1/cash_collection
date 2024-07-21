# Cash Collection

## Project Features
- User Authentication: Secure login and registration for users.
- User Profile Management: Update user profiles and manage user data.
- Cash Collection Management: Track and manage cash collections.
- Payment Tracking: Record and monitor payments.
- Reports: Generate detailed reports on cash collections and payments.
- Multi-language Support: Localized content for multiple languages.

## Endpoints

- `GET /api/tasks/`: Get all tasks.
- `GET /api/tasks/next_task/`: Get the next task for the logged-in CashCollector.
- `POST /api/collections/`: Collect cash for a specific task.
- `POST /api/pay/`: Deliver collected cash to a Manager.
- `GET /api/users/{id}/`: Get user details.
- `GET /api/cash-collectors/{id}/status/`: Get the freeze status of a user.
- `GET /api/cash-collectors/{id}/status-log/`: Get a cash collector's status logs.
- `GET /api/cash-collectors/`: Get the cash collectors list.
- `GET /api/cash-collectors/?frozen=true`: Get the frozen cash collectors list.
- `POST /api-token-auth/`: Login and get the access token

## Environment Variables

- `CASH_THRESHOLD`: The cash amount threshold to freeze a CashCollector (default: 5000 USD).
- `FREEZE_PERIOD`: The number of days to freeze a CashCollector after exceeding the cash threshold (default: 2 days).

## Setup

### Prerequisites
- Docker
- Docker Compose
- pre commit

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/TEha1/cash_collection.git
   cd cash_collection
   ```
2. Build and run the application with Docker:
    ```sh
    docker compose up --build
    ```

3. Access the application at `http://localhost:8000`.


## Development

### Apply Migrations

To apply migrations:

```sh
docker compose run web python manage.py migrate
```

To create superuser:

```sh
docker compose run web python manage.py createsuperuser
```

Before any push runs the pre-commit:

```sh
pre-commit run -a
```

## Testing

Run tests with:
```bash
docker compose run web coverage run manage.py test
