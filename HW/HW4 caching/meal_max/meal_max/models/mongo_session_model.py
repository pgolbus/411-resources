import logging
from typing import Any, List

from meal_max.clients.mongo_client import sessions_collection
from meal_max.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


class MongoSessionModel:

    @staticmethod
    def login_user(user_id: int, battle_model) -> None:
        """
        Load the user's combatants from MongoDB into the BattleModel's combatants list.

        Checks if a session document exists for the given `user_id` in MongoDB.
        If it exists, clears any current combatants in `battle_model` and loads
        the stored combatants from MongoDB into `battle_model`.

        If no session is found, it creates a new session document for the user
        with an empty combatants list in MongoDB.

        Args:
            user_id (int): The ID of the user whose session is to be loaded.
            battle_model (BattleModel): An instance of `BattleModel` where the user's combatants
                                        will be loaded.
        """
        session = sessions_collection.find_one({"user_id": user_id})
        if session:
            # Clear any previous combatants in the model
            battle_model.clear_combatants()
            for combatant in session.get("combatants", []):
                battle_model.prep_combatant(combatant)
        else:
            sessions_collection.insert_one({"user_id": user_id, "combatants": []})

    @staticmethod
    def logout_user(user_id: int, battle_model) -> None:
        """
        Store the current combatants from the BattleModel back into MongoDB.

        Retrieves the current combatants from `battle_model` and attempts to store them in
        the MongoDB session document associated with the given `user_id`. If no session
        document exists for the user, raises a `ValueError`.

        After saving the combatants to MongoDB, the combatants list in `battle_model` is
        cleared to ensure a fresh state for the next login.

        Args:
            user_id (int): The ID of the user whose session data is to be saved.
            battle_model (BattleModel): An instance of `BattleModel` from which the user's
                                        current combatants are retrieved.

        Raises:
            ValueError: If no session document is found for the user in MongoDB.
        """
        combatants_data = battle_model.get_combatants()
        result = sessions_collection.update_one(
            {"user_id": user_id},
            {"$set": {"combatants": combatants_data}},
            upsert=False  # Prevents creating a new document if not found
        )

        # Check if a document was actually modified (i.e., user was found)
        if result.matched_count == 0:
            logger.error("User %s not found in MongoDB for logout.", user_id)
            raise ValueError(f"User with ID {user_id} not found for logout.")

        # Clear the combatants from the model after successfully logging out
        battle_model.clear_combatants()
