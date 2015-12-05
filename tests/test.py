import os
import tempfile
import unittest

import dashydeebee

class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, dashydeebee.app.config['DATABASE'] = tempfile.mkstemp()
        dashydeebee.app.config['TESTING'] = True
        self.app = dashydeebee.app.test_client()
        dashydeebee.views.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(dashydeebee.app.config['DATABASE'])
    
    def test_first_test(self):
        rv = self.app.get('/activity/2015-08-01/2015-08-31')
        assert 'MDM Nepal' in rv.data.decode('utf-8')

if __name__ == '__main__':
    unittest.main()
