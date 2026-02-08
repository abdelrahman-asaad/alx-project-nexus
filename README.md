Nexus Invoice Management System
Project Overview
Nexus is an enterprise-grade invoice management system designed with a focus on scalability, security, and performance. The system leverages a modern asynchronous architecture to handle financial operations, automated communications, and complex data querying.

Technical Architecture
The system is built using a microservices-ready monolithic architecture, fully containerized using Docker.

Backend Framework: Django 5.2

API Layers: GraphQL (Graphene) and REST (Django Rest Framework)

Task Queue: Celery with Redis Broker

Database: PostgreSQL 15 with specialized indexing

Documentation: OpenAPI / Swagger

Core Systems and Features
1. Role-Based Access Control (RBAC)
The system implements a granular permission layer to ensure data integrity and security:

Admin Role: Full access to system configurations, user management, and global financial reports.

Manager Role: Authority to approve invoices, manage clients, and view team-level analytics.

User Role: Limited to creating and managing their own assigned invoices and client interactions.

Permissions: Custom Django permissions are applied at both ViewSet (REST) and Resolver (GraphQL) levels.

2. Background Tasks and Email Integration
To maintain a high-performance user experience, time-consuming operations are offloaded to Celery workers:

Asynchronous Processing: Operations like PDF generation and mass data exports are handled in the background.

Email System: Integrated with Gmail SMTP for automated account activation, password resets, and invoice delivery.

Retry Logic: Implemented for failed email tasks to ensure reliable communication.

3. API Performance and Optimization
GraphQL Payloads: Optimized queries to prevent the N+1 problem, allowing clients to request specific payloads and nested data in a single round-trip.

Database Indexing: Critical fields such as invoice_number, client_email, and created_at are indexed to ensure sub-second query execution on large datasets.

4. Security and Rate Limiting
The system is protected against brute-force attacks and API abuse through Django Rest Framework Throttling:

Anonymous Throttling: 10 requests per day per IP.

User Throttling: 1,000 requests per day for authenticated users.

Login Throttling: 5 attempts per minute to mitigate credential stuffing attacks.

API Documentation and Testing
API Specification
Swagger UI: Accessible at /swagger/ for interactive REST API exploration.

ReDoc: Accessible at /redoc/ for detailed documentation.

GraphQL Playground: Accessible at /graphql/ for schema introspection and query testing.

Testing Strategy
The project follows a rigorous testing protocol using pytest and unittest:

Automation Testing: Suite of integration tests covering the full invoice lifecycle.

Throttling Unit Tests: Specialized test cases to verify that rate limits are correctly enforced and return 429 Too Many Requests.

Logic Validation: Ensuring calculations for taxes, discounts, and totals are mathematically accurate.

DevOps and CI/CD
GitHub Actions Integration
The project includes a robust CI/CD pipeline defined in .github/workflows/:

Continuous Integration: Every push or pull request triggers automated linting (Flake8) and the full test suite.

Environment Consistency: Docker-based testing ensures that the CI environment exactly matches the production environment.

Deployment Pipeline
Build: Docker images are built and scanned for vulnerabilities.

Test: Automated execution of all unit and integration tests.

Deploy: Successful builds are automatically prepared for staging/production deployment.

User Interface
Basic Frontend Templates
While the core is a headless API, the system includes integrated Django templates for essential user-facing pages:

Authentication Pages: Styled login, registration, and password recovery forms.

Invoice Previews: Responsive HTML templates for viewing invoices before export to PDF.

Admin Dashboard: Standardized interface for system oversight.

Installation and Execution
Environment Setup
Clone the repository and create a .env file with the following variables:

Plaintext
POSTGRES_DB=your_db
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_app_password
Running the System
Bash
# Build and start all services
docker compose -f docker-compose.dev.yml up -d --build

# Apply migrations
docker compose -f docker-compose.dev.yml exec web python manage.py migrate

# Run Automated Tests
docker compose -f docker-compose.dev.yml exec web pytest
Author: Asaad License: MIT License