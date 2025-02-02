# multistore_api

## Overview

`multistore_api` is a Django-based backend API designed to manage multiple stores. It provides endpoints for managing products, orders, customers, and more.

## Features

- User authentication and authorization
- CRUD operations for products, orders, and customers
- Store management
- Order processing
- RESTful API design

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/multistore_api.git
    cd multistore_api
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Apply migrations:

    ```bash
    python manage.py migrate
    ```

5. Create a superuser:

    ```bash
    python manage.py createsuperuser
    ```

6. Run the development server:

    ```bash
    python manage.py runserver
    ```

## Usage

After starting the development server, you can access the API at `http://127.0.0.1:8000/`. Use tools like Postman or cURL to interact with the endpoints.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
