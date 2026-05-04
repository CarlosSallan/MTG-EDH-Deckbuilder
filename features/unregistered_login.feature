Feature: Login

  Scenario: Unregistered user logs in.
    Given a unregistered user
    When I go to the login page
    And I fill the form with valid credentials of an existing user
    And I press "Login"
    Then I should logged in