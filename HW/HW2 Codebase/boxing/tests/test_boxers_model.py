import unittest
from boxing.models import boxers_model


class TestBoxersModel(unittest.TestCase):

    def setUp(self):
        from boxing.utils.sql_utils import get_db_connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM boxers")
            conn.commit()
    
    def test_create_and_get_boxer(self):
        boxer_id = boxers_model.create_boxer("Aarnav", 160, 185, 78.5, 21)
        boxer = boxers_model.get_boxer_by_id(boxer_id)
        self.assertIsNotNone(boxer)
        self.assertEqual(boxer.name, "Aarnav")  # FIXED

    def test_get_boxer_by_invalid_id(self):
        with self.assertRaises(ValueError):
            boxers_model.get_boxer_by_id(-1)

    def test_get_boxer_by_name(self):
        boxers_model.create_boxer("Taha", 155, 178, 76, 20)
        boxer = boxers_model.get_boxer_by_name("Taha")
        self.assertIsNotNone(boxer)
        self.assertEqual(boxer.weight, 155)  # FIXED

    def test_duplicate_names_not_allowed(self):
        boxers_model.create_boxer("Aarnav", 160, 185, 78.5, 21)
        with self.assertRaises(Exception):
            boxers_model.create_boxer("Aarnav", 300, 201, 80, 96)

    def test_delete_boxer(self):
        boxer_id = boxers_model.create_boxer("Canelo", 185, 180, 75, 29)
        boxers_model.delete_boxer(boxer_id)
        with self.assertRaises(ValueError):  # FIXED
            boxers_model.get_boxer_by_id(boxer_id)


if __name__ == "__main__":
    unittest.main()
