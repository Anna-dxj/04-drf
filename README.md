# Django (MVT) Assignment

Develop a Django web application that utilizes the database schema from your previous project (e-commerce backend). Create Django models based on the entities, set up views to handle business logic, and design templates to display data to users. 

## Requirements
1. Set up the Django project
    - create a new Django project
    - Set up a new Django app within the project
    - Configure project to connect to the Postgres database previously designed. Ensure that the database settings in `settings.py` match your existing Postgres database
2. Create Django Models
    - Convert each database entity into Django models
    - Ensure each relationship is appropriately reflected in DJango models using fields like `ForeignKey`, `OneToOneField`, and `ManyToManyField`.
    - Include model methods where appropriate, such as methods for calculating tools or generating reports
3. Implementing custom querysets
    - Write custom querysets/methods in models to perform complex queries:
4. Setting up Django Admin
    - Register models with the Django admin sight
    - Customize admin interface to make it user-friendly, such as by defining list displays, search fields, and filters
5. Creating Views
    - Implement views to handle business logic of application:
        - List View to list all entities
        - Details View to show details of a specific entity
        - Create/Edit Views to allow adding or editing entities 
    - Use Django's built-in CBV when applicable 
6. Designing Templates
    - Create HTML templates to display data. Templates should be user-friendly and reflect the structure of models
    - Include forms in your templates to allow users to add or edit dat (eg. create a new product)
    - Implement navigation between different parts of application 
7. Testing Application
    - Test application to ensure that all views work as expected and the data is being manipulated correctly 
8. Documentation
    - Documetn code with docstrings nad comments explaining the purpose of each model, view, and template

## Submission
- Code:
    - Submit the Django project folder, including all apps, models, views, templates, and static files via GitHub
- Live Presentation
    - Walk through functionality and explain how schema was integrated into the Django Project 