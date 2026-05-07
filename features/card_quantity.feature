Feature: Card Quantity

    Scenario: Changing card quantity to zero.
        Given a deck owned by user
        When I change the quantity to zero
        Then the quantity should not change
    Scenario: Changing card quantity.
        Given a deck owned by user
        When I change the quantity
        Then the quantity should change

