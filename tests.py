
from app import create_app, db
from app.models import User, Budget_Category, Budget_History, Transaction
from config import Config
from datetime import datetime, timedelta
import unittest

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_transaction_apply(self):
        b = Budget_Category(category_title='b',
                    current_balance=100
                    )
        db.session.add(b)
        db.session.commit()

        te = Transaction(id_budget_category=b.id,
                        amount=50,
                        ttype='E')
        db.session.add(te)

        ti = Transaction(id_budget_category=b.id,
                        amount=50,
                        ttype='I')
        db.session.add(ti)
        db.session.commit()

        te.apply_transaction()
        self.assertEqual(b.current_balance, 50)
        ti.apply_transaction()
        self.assertEqual(b.current_balance,100)

    def test_transaction_unapply(self):
        b = Budget_Category(category_title='b',
                    current_balance=100
                    )
        db.session.add(b)
        db.session.commit()

        te = Transaction(id_budget_category=b.id,
                        amount=50,
                        ttype='E')
        db.session.add(te)

        ti = Transaction(id_budget_category=b.id,
                        amount=50,
                        ttype='I')
        db.session.add(ti)
        db.session.commit()

        te.unapply_transaction()
        self.assertEqual(b.current_balance, 150)
        ti.unapply_transaction()
        self.assertEqual(b.current_balance, 100)

    def test_change_trans_amount(self):
        b = Budget_Category(category_title='b',
            current_balance=100
            )
        db.session.add(b)
        db.session.commit()

        te = Transaction(id_budget_category=b.id,
                        amount=50,
                        ttype='E')
        db.session.add(te)

        ti = Transaction(id_budget_category=b.id,
                        amount=50,
                        ttype='I')
        db.session.add(ti)
        db.session.commit()

        te.change_trans_amount(25)
        self.assertEqual(b.current_balance,125)
        ti.change_trans_amount(25)
        self.assertEqual(b.current_balance,100)

    
    def test_change_trans_type(self):
        b = Budget_Category(category_title='b',
            current_balance=100
            )
        db.session.add(b)
        db.session.commit()

        te = Transaction(id_budget_category=b.id,
                        amount=50,
                        ttype='E')
        db.session.add(te)
        db.session.commit()   

        te.change_trans_type()
        self.assertEqual(b.current_balance,200)
        te.change_trans_type()
        self.assertEqual(b.current_balance,100)     

    def test_change_trans_category(self):
        b = Budget_Category(category_title='b',
            current_balance=100
            )
        db.session.add(b)

        c = Budget_Category(category_title='c',
            current_balance=100
            )
        db.session.add(c)
        db.session.commit()

        te = Transaction(id_budget_category=b.id,
                        amount=50,
                        ttype='E')
        db.session.add(te)
        db.session.commit() 

        te.change_trans_category(c.id)
        self.assertEqual(b.current_balance,150)
        self.assertEqual(c.current_balance,50)       

    def test_cascade_delete(self):
        b = Budget_Category(category_title='b',
                            current_balance=100
                            )
        db.session.add(b)
        db.session.commit() 

        h = Budget_History(id_budget_category = b.id,
                            status='C',
                            annual_budget=1000
                            )
        db.session.add(h)
        db.session.commit() 

        db.session.delete(b)
        db.session.commit()
        self.assertFalse(h.id)




if __name__ == '__main__':
    unittest.main(verbosity=2)