import app
import unittest
import migrate


class IndexPageTestCase(unittest.TestCase):

    def setUp(self):
        migrate.init_db()
        self.app = app.app.test_client()

    def tearDown(self):
        migrate.drop_db()

    def test_index_page_emtpy(self):
        rv = self.app.get('/')
        assert "No popular games" in str(rv.data)
        assert "No recent scores" in str(rv.data)

    def test_add_game(self):
        create_game(self.app, "TestGame")
        rv = self.app.get('/game/')
        assert "TestGame" in str(rv.data)

        # The Game's page
        rv = self.app.get('/game/TestGame/')
        assert "TestGame" in str(rv.data)

        # Leaderboard
        rv = self.app.get('/game/TestGame/leaderboard/')
        assert "TestGame Leaderboard" in str(rv.data)


def create_game(app, gameName):
    app.post('/game/',
             data=dict(gameName=gameName))


if __name__ == '__main__':
    unittest.main()
