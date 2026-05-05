Feature: Logout

    Scenario: Logged user logs out.
        Given a registered user
        When press "Logout"
        Then should be logged out
