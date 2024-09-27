# DRF Assignment

## Description
This project is an ecommerce application built with Django and Django REST Framework (DRF) capabilities. It provides a platform both for vendors to manage their products and customers to browse and purchase items. This application features user authentication, vendor management, and product management.

###  Features
- User authentication: Users can register through our site, login through traditional means or with a google account, and manage their profile. 
- Vendor management: vendors are able to create, update, and delete their product listings, as well as monitor product stock and their top-selling products.
- Product mmanagement: users are able to browse products, filter by category, as well as look at suggested products based on their browsing history.
- Category management: products are organized into catgories, to make it easier for users to find what they're looking for 
- Rate limiting: the api associated with this application includes throttling for anonomous and authenticated users
- Permissions: custom permissions have been used to ensure vendors are able to modify their own products and customers are able to modify information associated with their account. 

### Technologies used:
- Django as the framework for buildign the application
- DJango REST Framework for building the api
- PostgreSQL as the database management system
- Django Filter to implement filtering and searching capabilities for the api
- Django Allauth for handling social account support

## API Endpoints:
- Products: `/api/products/`
    Only a owning vendor is able to perform create, update, delete operations on their own product, but a non-owning, non-vendor is able to perform read operations. 
    Products API endpoint has filtering, searching, and ordering capabilities. Products are able to be filtered by `category` or `vendor` ids, searched by `name` and `description` fields, and ordered by `price`.
- Categories: `/api/categories/`
    Only admin users are able to perform create, update, delete operations, but a non-admin user is able to perform read operations.
    Categories API endpoint has searching and ordering capabilities. Categories are able to be searched and ordered by `name`.
- Vendors: `/api/vendors/`
    Only vendors are able to perform create, update, delete operations on their associated vendor instance, but non-owning, non-vendors are able to perform read operations. 
    Vendor API endpoint has searching and ordering capabilities. Vendors are able to be searched by `company_name` and `description` fields, and ordered by `company_name`. 
- Customer: `/api/customers/`
    Only a owning customer is able to perform create, update, delete operations on their associated customer instance. A customer is also only able to perform read operations on thier associated account. A non-owning admin user is able to perform read operations on all accounts.
- User: `/api/users/`
    Only a owning user is able to perform create, update, delete operations on their associated user. A user is only able to perform read operations on their associated user. A non-owning admin user is able to perform read operations on all accounts.
- Default shipping: `/api/shipping/`
    Only a owning customer is able to perform create, update, and delete operations on their associated default shipping address. A customer is only able to perform read operations on their associated shipping address. A non-owning admin user is able to perform read operations on all shipping instances.
- Special Shipping: `/api/special-shipping/`
    Only an owning customer is able to perform create, update, and delete operations on a non-default shipping address for an associated order. A customer is only able to perform read operations on non-default shipping addresses associated with orders with their account. A non-owning admin user is able to perform read operations on all non-default shipping instances associated with any account.
- Order Details: `/api/order-detail/`
    Only a owning customer is able to perform create, update, and delete operations on order details for an associated order. A customer is only able to perform read operations on order details for orders associated with their account. A non-owning admin user is able to perform read operations on order details associated with any order.
- Order: `api/orders`
    Only a owning customer is able to perform create, update, adn delete operations on an order associated with their account. A customer is only able to perform read operations on an order associated with their own account. A non-owning admin user is able to perform read operations on an order associated with any account.
- Payment: `api/payment`
    Only admin users are able to perform create, update, delete operations, but a non-admin user is able to perform read operations.

## Installation
1. clone [repository](https://github.com/Anna-dxj/04-drf)
2. Create a virtual environment
3. Install required packages: `pip install -r requirements.txt`