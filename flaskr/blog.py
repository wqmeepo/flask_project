from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from .auth import login_required
from .db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    database = get_db()
    posts = database.execute(
        'select a.id, a.title, a.body, a.created, a.author_id, b.username from post a '
        'inner join user b on a.author_id = b.id order by a.created desc'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

    if not title:
        error = 'Title is required'

    if error is not None:
        flash(error)
    else:
        database = get_db()
        database.execute(
            'insert into post(title, body, author_id) values (?,?,?)',
            (title, body, g.user['id'])
        )
        database.commit()
        return redirect(url_for('blog.index'))
    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'select a.id, a.title, a.body, a.created, a.author_id, b.username from post a '
        'inner join user b on a.author_id = b.id where a.id=?', (id,)).fetchone()
    if post is None:
        abort(404, f'post id {id} doesn`t exist')

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'title is required'

        if error:
            flash(error)
        else:
            database = get_db()
            database.execute(
                'update post set title=?, body=? where id=?', (title, body, id)
            )
            database.commit()
            return redirect(url_for('blog.index'))

        return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST', ))
@login_required
def delete(id):
    get_post(id)
    database = get_db()
    database.execute(
        'delete from post where id=?', (id, )
    )
    database.commit()
    return redirect(url_for('blog.index'))
