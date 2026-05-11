# Deliverable 2 — Web 2.0 Application Development

Continuing with the Web application developed for the first deliverable,
incorporate the basic mechanisms to convert it into a Web 2.0 application.

## Features to add (end-user, without Django admin)

- **(3 Points)** Allow registered users to create new instances of model entities,
  as long as it makes sense that users create them.
- **(3 Points)** Allow users to modify entity instances, for example that they
  can modify instances created by them.
- **(1.5 Points)** Allow users to delete instances of model entities,
  usually those created by them.

In all of these cases (creation, update and deletion) there should be **end-to-end
tests (E2E)** for the corresponding features of the application. These tests should
verify correct behavior but also how errors are managed or relevant security
restrictions addressed. It is recommended to use **Behave** and **Splinter** for the
E2E tests as in the example project, myrestaurants.

- **(2.5 Points)** Incorporate data from an external API in the operation of the
  application. For example, one of the forms used to create or modify instances uses
  this data to assist users while editing using AJAX (by means of the JQuery library).

> Note: It is also recommended to use ClassViews and ModelForms to implement the
> creation, update and delete features. More details are available from the tutorials
> available from the Resources section of the Virtual Campus: "Django Web 2.0 Tutorial".

## Code Delivery

The code must be available in the github.com repository created for the first delivery.
This repository should be used with a different user for each member of the project group.

Please provide access to the repository to GitHub user: **rogargon**

## Documentation to deliver

A document detailing:

1. Public address of the GitHub repository.
   - Please commit the database (`db.sqlite3`) to facilitate testing the application.
2. Admin user password and other relevant users to test the application.
3. Details about design considerations and decisions important for the evaluation,
   for example changes in the model compared to the first deliverable.

All members of the group should submit the project via the Virtual Campus.
