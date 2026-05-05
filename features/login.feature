Feature: Login

  Scenario: Unregistered user logs in.
    Given a unregistered user
    When I go to the login page
    And I fill the form with valid credentials of an existing user
    And I press "Login"
    Then I should logged in

  Scenario: User fails login with wrong password
  Given a unregistered user
  When I go to the login page
  And I fill the form with invalid credentials
  And I press "Login"
  Then the login should fail

  Scenario: User fails login with non-existing account
  Given a non-existent user
  When I go to the login page
  And I fill the form with nonexisting credentials
  Then the login should fail

  Scenario: User submits empty login form
  When I go to the login page
  And I press "Login"
  Then the login should fail