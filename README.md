# Agrovet Inventory Management API

A Flask-based REST API for managing inventory at a small agrovet (farm/poultry supplies) retail shop. Includes CRUD operations, integration with the OpenFoodFacts external API, and a CLI tool for interacting with the system.

## Features

- Full CRUD for inventory items (Create, Read, Update, Delete)
- Search and import real product data from the OpenFoodFacts API
- Command-line interface for managing inventory without needing Postman
- Mock in-memory database (resets on server restart)

## Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/decherulo/inventory-management-api.git
   cd inventory-management-apipython3 -m venv venv
source venv/bin/activate