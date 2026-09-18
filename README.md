API Simulator

Overview

API Simulator is a full-stack platform designed to help developers create and test simulated HTTP APIs without building a real backend for every endpoint.

The platform provides a simple workspace where developers can define an API, configure its versions and request contracts, create different response scenarios, control access, send test requests, and review request activity from a centralized dashboard.

The main goal of the project is to make API development and frontend integration easier by allowing teams to simulate backend behavior during development and testing.

Backend

Technology Stack

Python 3.12

FastAPI

SQLAlchemy

MySQL 8.0

Alembic

Redis

Pydantic

JWT Authentication

Uvicorn

Docker

Backend Architecture


The backend follows a layered architecture to keep API handling, business logic, database access, validation, and dynamic request processing separated.

API Layer

The FastAPI routes provide endpoints for:

Authentication

User management

API management

API versions

Request contracts

Response scenarios

Permissions

Request logs

Dashboard statistics

Service Layer

The service layer contains the application's business logic.

It handles:

User authentication

API creation and management

Version management

Request validation

Response scenario processing

Permission management

Request logging

Dashboard calculations

Caching

Dynamic endpoint execution

Repository Layer

Repositories are responsible for database operations and keep SQL/database logic separate from the service layer.

The backend manages the following main entities:

Users

Mock APIs

API versions

Request schemas

Response templates

Request logs

API permissions

Dynamic API Runtime

One of the main features of the backend is dynamic endpoint handling.

Instead of defining every simulated API as a hardcoded FastAPI route, the runtime loads API definitions from the database and matches incoming requests against the configured method and path.

The runtime then:

Identifies the configured API.

Resolves the active version.

Validates the incoming request.

Checks access requirements.

Selects the configured response scenario.

Applies the configured delay.

Builds the response.

Records the request in the request history.

This allows developers to create and modify simulated APIs through the application instead of changing backend source code.

Authentication and Security

The backend uses JWT-based authentication.

Authenticated users can access protected application features, while API-level permissions can control access to private simulated endpoints.

The backend also includes:

Password hashing

Token validation

Protected routes

Role-based access restrictions

API-level permissions

Request validation

Centralized exception handling

API Versioning

Each API can contain multiple versions.

Versions can be activated or deactivated independently, allowing developers to maintain different API contracts and responses while testing changes safely.

The dynamic runtime uses the active version when processing requests.

Request Contract

Each API version can define how incoming requests should be handled.

The contract supports:

Query parameters

Path parameters

Headers

Request body schemas

Required fields

Data types

Validation rules

This allows the simulator to reproduce realistic backend validation behavior.

Response Scenarios

Developers can configure different responses for an API.

Supported scenarios include:

Success

Validation Error

Unauthorized

Not Found

Server Error

Custom scenarios

Each response can contain:

HTTP status code

Response headers

Response body

Response delay

This makes it possible to test both successful and failure conditions from the frontend.

Request Logging

Every request processed by the dynamic runtime can be recorded.

The request history contains information such as:

Endpoint

HTTP method

Parameters

Request body

Response status

Response time

Timestamp

This information is used by the dashboard and request logs interface.

Dashboard

The backend provides dashboard statistics including:

Total APIs

Active APIs

Total requests

Error requests

Most-used endpoints

Average response time

Error rate

The frontend displays these values using data received from the authenticated backend.

Redis

Redis is used as a caching layer for dynamic API definitions and runtime-related data.

The caching layer helps reduce unnecessary database lookups while keeping API definitions synchronized when configuration changes.

Database

MySQL stores the application's persistent data.

The primary tables are:

users

mock_apis

api_versions

request_schemas

response_templates

request_logs

api_permissions

Database schema changes are managed using Alembic migrations.

Frontend

Technology Stack

React

TypeScript

Vite

Material UI

Axios

React Router

Recharts

Frontend Architecture

The frontend is designed as a developer-focused API workspace with a dark interface and high-contrast visual system.

It communicates with the FastAPI backend through Axios and uses authenticated API requests for application data.

The frontend does not depend on hardcoded dashboard statistics or API records. Data is loaded from the backend.

Main Frontend Areas
Dashboard

The dashboard provides a quick overview of the current workspace.

It displays:

Total APIs

Active APIs

Requests

Errors

Most-used endpoints

Average response time

Error rate

The information is generated from backend data.

API Catalog

The API catalog allows users to:

Create APIs

View APIs

Edit APIs

Activate APIs

Deactivate APIs

Delete APIs

Open API configuration

Each API displays its method, endpoint, access type, status, and update information.

API Versions

Users can create and manage multiple versions of an API.

The interface displays the active state of each version and provides access to its configuration.

Request Contract

The contract editor provides a UI for configuring:

Query parameters

Path parameters

Headers

Request body schema

The configuration is persisted through the backend.

Response Scenarios

Users can configure different response behaviors for each API version.

This provides a convenient way to test successful responses as well as different API failure conditions.

Permissions

Private APIs can have access permissions configured through the frontend.

This allows API owners to control which users can access protected simulated endpoints.

Request Lab

Request Lab acts as an interactive API testing workspace.

Developers can select an API and version, configure request information, execute the request, and inspect the response.

It displays:


HTTP status

Response time

Response body

Response headers

It also provides the ability to generate multiple requests for testing and traffic simulation.

Request Logs

Request Logs provides visibility into previously executed requests.

Developers can inspect request activity and use the information to understand API usage and response behavior.

Workspace

The workspace contains application-level settings and authenticated user information.

Frontend–Backend Communication

The frontend communicates with the FastAPI backend through REST APIs.

Axios is responsible for HTTP communication and authentication handling.

The general flow is:

React UI

   ↓
Axios API Client

   ↓
FastAPI

   ↓
Service Layer

   ↓
   
Repository Layer
   ↓
   
MySQL

For simulated API execution:

Request Lab

   ↓
Dynamic Runtime

   ↓
API Definition

   ↓
Request Validation

   ↓
Scenario Selection

   ↓
Response


   ↓
Request Log


Error Handling

The backend uses centralized application exceptions and exception handlers to provide consistent API error responses.

The frontend displays backend errors through the application interface instead of exposing raw server errors to the user.

Validation errors, authentication errors, permission errors, missing APIs, inactive APIs, and runtime errors are handled through the application's error-handling flow.

Testing

The project includes backend unit and integration testing areas covering:

Authentication

API management

Dynamic endpoints

Request validation

Response scenarios

Dashboard behavior


API testing can also be performed through Swagger/OpenAPI and Postman.

Docker

The project includes Docker configuration for running the application services in a consistent development environment.

The environment is designed around:

FastAPI backend

MySQL database

Redis

React frontend

Environment-specific configuration is managed through environment variables.

Project Goal

API Simulator brings API creation, configuration, testing, and monitoring into one developer workspace.

Instead of repeatedly creating temporary backend endpoints for frontend development, developers can configure simulated APIs through the platform and immediately test different request and response behaviors.

The project combines dynamic API execution, request validation, response simulation, versioning, authentication, permissions, logging, caching, and analytics into a single full-stack application.
