import pytest
from src.database import User, Post, Comment, db

@pytest.fixture(scope='module')
def new_user():
    user = User(username='testuser', email='testuser@example.com')
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()

@pytest.fixture(scope='module')
def new_post(new_user):
    post = Post(title='Test Post', content='This is a test post.', author=new_user)
    db.session.add(post)
    db.session.commit()
    yield post
    db.session.delete(post)
    db.session.commit()

@pytest.fixture(scope='module')
def new_comment(new_user, new_post):
    comment = Comment(content='This is a test comment.', author=new_user, post=new_post)
    db.session.add(comment)
    db.session.commit()
    yield comment
    db.session.delete(comment)
    db.session.commit()

def test_user(new_user):
    assert new_user.username == 'testuser'
    assert new_user.email == 'testuser@example.com'

def test_post(new_post):
    assert new_post.title == 'Test Post'
    assert new_post.content == 'This is a test post.'
    assert new_post.author.username == 'testuser'

def test_comment(new_comment):
    assert new_comment.content == 'This is a test comment.'
    assert new_comment.author.username == 'testuser'
    assert new_comment.post.title == 'Test Post'