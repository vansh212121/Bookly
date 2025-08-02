# Bookly:  A Modern REST API

Bookly is a feature-rich, production-grade REST API for a social book review platform. This project was developed as a deep dive into building a robust, secure, and scalable backend service using a modern Python technology stack. It goes beyond a simple CRUD application to implement the architectural patterns and best practices found in real-world, high-performance services.

The core of the application is a clean, 3-tier architecture (Endpoints → Services → CRUD) that ensures a clear separation of concerns, making the codebase maintainable, testable, and scalable.

---

## Core Features

* **Advanced Authentication:** JWT-based system with Access/Refresh Tokens, secure "sliding sessions" via Refresh Token Rotation, and server-side logout.
* **Flexible Authorization:** Scalable, Enum-based Role-Based Access Control (RBAC) to protect endpoints.
* **Full User Lifecycle:** Complete flow from user signup with email verification to secure password resets.
* **Asynchronous Background Tasks:** Celery and Redis handle slow operations like sending emails, ensuring the API remains fast and responsive.
* **Professional Middleware Stack:** For security, performance, and observability, including CORS, GZip, and structured request/response logging with tracing IDs.
* **Robust Error Handling:** A centralized system with custom exceptions for clean, consistent, and meaningful error responses.
* **Database Management:** Safe and repeatable schema migrations managed by Alembic.
* **Fully Asynchronous:** Built from the ground up with `async`/`await` for high performance and concurrency.

---

## Technology Stack

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) for its high performance and modern Python features.
* **Database ORM:** [SQLModel](https://sqlmodel.tiangolo.com/) for its combination of Pydantic data validation and SQLAlchemy's power.
* **Database:** [PostgreSQL](https://www.postgresql.org/) (running in Docker) as the primary relational database.
* **Migrations:** [Alembic](https://alembic.sqlalchemy.org/) for managing database schema changes.
* **Authentication:** [Passlib](https://passlib.readthedocs.io/) and [Bcrypt] for password hashing, [python-jose](https://github.com/mpdavis/python-jose) for JWTs, and the OAuth2 Password Bearer flow.
* **Background Tasks:** [Celery](https://docs.celeryq.dev/) for the task queue and [Redis](https://redis.io/) (running in Docker) as the message broker.
* **Task Monitoring:** [Flower](https://flower.readthedocs.io/) for a real-time web dashboard to monitor Celery workers and tasks.
* **Testing:** [Pytest](https://docs.pytest.org/) with `pytest-asyncio` and `httpx` for a fully asynchronous integration test suite.

---

## Key Architectural Highlights

### Authentication & Security

The authentication system was designed to be both highly secure and user-friendly.

* **Dual Token System:** Upon login, the API issues a short-lived **Access Token** (e.g., 15 minutes) and a long-lived **Refresh Token** (e.g., 30 days). The access token is used for all authenticated API calls, minimizing the risk of a stolen token.
* **Refresh Token Rotation (Sliding Sessions):** To keep users logged in seamlessly, the `/refresh` endpoint accepts a valid refresh token and returns a *brand new* access token and a *brand new* refresh token. The old refresh token is immediately invalidated. This provides a "sliding session" that can last indefinitely as long as the user is active, while also providing reuse detection to protect against token theft.
* **Server-Side Logout:** The `/logout` endpoint provides true token revocation. It adds the unique ID (`jti`) of the user's token to a **Redis blocklist**. All protected endpoints check this blocklist, ensuring that a logged-out token is instantly invalidated, even if it hasn't expired.

### Flexible Authorization (RBAC)

Authorization is handled by a clean, scalable Role-Based Access Control (RBAC) system.
* The `User` model has a flexible `role` field (e.g., `USER`, `ADMIN`) instead of a simple boolean flag.
* A reusable, class-based `RoleChecker` dependency is used in endpoint decorators to protect routes based on a list of allowed roles (e.g., `dependencies=[Depends(RoleChecker([UserRole.ADMIN]))]`). This makes the permission logic clean, declarative, and easy to extend with new roles in the future.

### Asynchronous Background Tasks

To ensure the API remains fast and responsive, any slow or non-essential operation is offloaded to a background worker.
* **Celery & Redis:** When a user signs up or requests a password reset, the API instantly returns a response. The job of sending the email is dispatched to a Celery task queue, with Redis acting as the message broker.
* **Flower Monitoring:** The Flower dashboard is integrated, providing a real-time web UI to inspect worker status, view task history, and debug background jobs.

---

## Setup and Installation

To run this project locally, you will need Python 3.10+, Docker, and Docker Compose installed.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
    cd your-repository-name
    ```

2.  **Create and configure the environment file:**
    * Copy the example environment file: `cp .env.example .env`
    * Edit the `.env` file and fill in your database credentials, JWT secret, and email server details.

3.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

4.  **Start the database and Redis services:**
    ```bash
    docker-compose up -d
    ```

5.  **Run database migrations:**
    ```bash
    alembic upgrade head
    ```

6.  **Run the application:**
    * **FastAPI Server (Terminal 1):**
        ```bash
        uvicorn app.main:app --reload
        ```
    * **Celery Worker (Terminal 2):**
        ```bash
        celery -A celery_worker.celery_app worker -P solo --loglevel=info
        ```

The API will be available at `http://localhost:8000`, with interactive documentation at `http://localhost:8000/docs`.
