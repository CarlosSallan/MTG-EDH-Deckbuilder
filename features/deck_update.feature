Feature: Deck Update

  Scenario: Owner updates their deck name
    Given a deck I own exists
    When I visit the edit page for my deck
    And I change the deck name to "e2e_renamed_deck" and submit
    Then the deck name should be "e2e_renamed_deck" in the database

  Scenario: User cannot edit another user's deck
    Given a deck owned by another user exists
    When I visit the edit page for the other user's deck
    Then I should see a not-found page
    And the other user's deck should remain unchanged

  Scenario: Submitting the edit form with an empty name does not change the deck
    Given a deck I own exists
    When I visit the edit page for my deck
    And I clear the deck name and submit
    Then I should still be on the deck edit page
    And the deck name should remain unchanged
