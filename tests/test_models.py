import unittest

from models.models import Base, Score, User, engine, get_session


class ModelsTest(unittest.TestCase):
    def setUp(self):
        # Start each test with a clean in-memory schema
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.session = get_session()

    def tearDown(self):
        self.session.close()

    def test_insert_entity(self):
        user = User(external_id="ext-123", name="Tester")
        self.session.add(user)
        self.session.commit()

        score = Score(game_mode=0, score=123, user=user)
        self.session.add(score)
        self.session.commit()

        scores = Score.query(self.session).all()
        self.assertEqual(1, len(scores))
        self.assertEqual(user.id, scores[0].user_id)


if __name__ == '__main__':
    unittest.main()
