"""
Unit tests for the boxing.models.boxers_model module.

This file tests the following functions and features:
  - create_boxer: Validates boxer creation with valid and invalid inputs.
  - delete_boxer: Ensures deletion works when the boxer exists and fails when not.
  - get_leaderboard: Verifies leaderboard retrieval with both valid and invalid sort parameters.
  - get_boxer_by_id / get_boxer_by_name: Tests retrieval of a boxer by ID and name.
  - get_weight_class: Confirms weight class determination for various weight inputs.
  - update_boxer_stats: Checks that boxer statistics are updated correctly for wins and losses.
External dependencies such as database connections are mocked via a FakeConnection.
"""