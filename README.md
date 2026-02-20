# 🎟 Event Management API

[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)  
[![Django](https://img.shields.io/badge/Django-5.x-green)](https://www.djangoproject.com/)  
[![Django REST Framework](https://img.shields.io/badge/DRF-REST--API-red)](https://www.django-rest-framework.org/)  
[![Docker](https://img.shields.io/badge/Docker-Containerized-blue)](https://www.docker.com/)  
[![Swagger](https://img.shields.io/badge/API-Docs-brightgreen)](#)

A production-oriented **RESTful Event Management API** built with Django and Django REST Framework.

This API allows users to create and manage events, purchase tickets, track transactions, and interact with the system securely using role-based permissions and token authentication.

The project is fully containerized using Docker and includes interactive API documentation via Swagger.

All endpoints can be explored and tested at: /api/docs/

---


## ✨ Project Overview

The Event Management API is designed to simulate a real-world event booking system.  

It handles:

- User authentication and role management  
- Event creation and ticket management  
- Payment status tracking  
- Transaction history  
- Advanced filtering and querying  
- Production-ready Docker setup  

The goal of this project was to build a clean, scalable backend system that reflects real application logic beyond basic CRUD operations.

---

## 🛠 Core Features

### 🔐 Authentication & Authorization
- User registration and login
- Token-based authentication
- Role-based access control
- Protected endpoints
- Custom permissions per user role

---

### 📅 Event Management
- Create, update, and delete events
- Associate events with organizers
- Manage ticket pricing and availability
- Structured validation and business logic enforcement

---

### 🎫 Ticket Booking & Payments Logic
- Users can book tickets for events
- Tracks ticket quantities per user
- Maintains payment status (e.g., pending, completed, failed)
- Prevents overbooking based on event capacity
- Stores transaction history per user

> Note: This project simulates payment status handling (no external payment gateway integration).

---

### 💳 Transaction History
- Users can view their booking history
- Tracks event name, ticket quantity, total price, and payment status
- Structured data relationships between users, events, and transactions

---

### 🔎 Advanced Filtering & Querying
The API supports flexible filtering and querying, including:

- Filter events by name
- Filter by price range
- Search events dynamically
- Ordering results
- Structured query parameter handling

This improves usability and simulates real production API behavior.

---

### 📄 Interactive API Documentation
- Integrated Swagger UI
- Self-documented endpoints
- Easy testing directly from the browser
- Clear request and response schemas

Access via: /api/docs/

---

## ⚙️ Tech Stack

### Backend
- Python 3.x
- Django 5.x
- Django REST Framework
- drf-spectacular / Swagger

### Database
- MySql (development)
- PostgreSQL-ready configuration

### Containerization
- Docker
- Docker Compose
- Environment variable configuration via `.env`

### Authentication
- Token-based authentication

### Development & Testing
- Postman
- Git & GitHub

---

## 🐳 Docker Setup

This project is fully containerized.

It includes:

- `Dockerfile`
- `docker-compose.yml`
- `.env.example`

### 🔧 Environment Setup

1️⃣ Copy the environment file:

```bash
cp .env.example .env
```

2️⃣ Update environment variables as needed.

---

## Steps to run locally:
This project is containerized using Docker. To run the project locally, you will need to have Docker installed on your machine.

```bash
docker-compose build
```
### Run all services
```bash
docker-compose up
```
### This will start:
- The API will be available at: http://localhost:8000
- The API will be available at: http://localhost:8000/api/docs/

### To stop:
```bash
docker-compose down
```

---

### 🩺 Health Check
A /health/ endpoint is included for container monitoring.

---

## 🧱 Project Architecture

The project follows a modular Django structure:

- **accounts** → User authentication and permissions  
- **events** → Event logic, ticket booking, and transactions  
- **core** → Project configuration and global settings  

This separation improves maintainability, scalability, and overall code clarity.

---

## 🛡 Production-Oriented Practices

- Environment-based configuration using `.env`
- Fully Dockerized setup (Dockerfile + docker-compose)
- Structured app separation following Django best practices
- Role-based permission system
- Payment status handling logic (pending, completed, failed)
- Advanced filtering and query optimization
- Interactive API documentation via Swagger

---

## 🎯 Learning Outcomes

- Designing scalable RESTful APIs  
- Implementing authentication and role-based permissions  
- Building ticket booking systems with payment status tracking  
- Managing relational data between users, events, and transactions  
- Implementing advanced filtering and structured query handling  
- Containerizing Django applications using Docker  
- Writing production-ready backend systems

---

## 👨‍💻 About the Developer

Hi! I’m **Sofi (Sofoniyas)** — a **Backend Developer** and **Software Engineering student at AASTU**, and a **graduate of the ALX Backend Engineering Program**.

I specialize in building **secure, scalable, and production-ready backend systems** using modern backend technologies. I enjoy translating real-world business requirements into clean, maintainable, and efficient backend solutions.

I’m particularly interested in:

- Backend system design and RESTful API development
- Authentication, authorization, and security best practices
- Writing clean, scalable, and maintainable backend architectures
- Building data-driven applications and backend services

This project showcases my growth in backend development and my ability to solve real-world problems with clean, maintainable code.

---

### 🤳 Connect with me

[<img align="left" alt="LinkedIn" width="22px" src="https://cdn.jsdelivr.net/npm/simple-icons@v3/icons/linkedin.svg" />][linkedin]  
[<img align="left" alt="GitHub" width="22px" src="https://cdn.jsdelivr.net/npm/simple-icons@v3/icons/github.svg" />][github]  

[linkedin]: https://linkedin.com/in/sofoniyas-alebachew-bb876b33b
[github]: https://github.com/sofi391