Feature: Deck Delete

  Scenario: Owner deletes their own deck
    Given a deck I own exists
    When I visit the delete URL for my deck
    Then my deck should be removed from the database

  Scenario: User cannot delete another user's deck
    Given a deck owned by another user exists
    When I visit the delete URL for the other user's deck
    Then I should see a not-found page
    And the other user's deck should still exist in the database
