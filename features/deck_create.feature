Feature: Deck Create

  Scenario: Logged-in user creates a deck with a valid commander
    Given I am logged in
    When I visit the deck create page
    And I fill the deck form with name "e2e_create_deck" and a valid commander
    And I submit the deck form
    Then a deck named "e2e_create_deck" should exist owned by me

  Scenario: Logged-in user submits an empty deck create form
    Given I am logged in
    When I visit the deck create page
    And I submit the deck form
    Then I should still be on the deck create page
    And no deck named "e2e_create_deck" should exist

  Scenario: Anonymous user is redirected to login from the deck create page
    Given I am not logged in
    When I visit the deck create page
    Then I should be redirected to the login page
