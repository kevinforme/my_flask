from flask_login import login_required, current_user

from app import db
from app.decorators import admin_required, permission_required
from app.main.forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from app.models import Permission, User, Role, Post, Comment
from . import main
from flask import current_app, abort, request, render_template, flash, redirect, url_for, jsonify


# 用来关闭应用的路由，测试专用
@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'shutting down...'


# 主页路由
@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POST_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    recommends = User.query.filter_by(recommend=True)
    return render_template('index.html', posts=posts, pagination=pagination, recommends=recommends)


# 仅查看关注者文章的路由
@main.route('/followed_posts')
@login_required
def followed_posts():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POST_PER_PAGE'], error_out=False)
    posts = pagination.items
    recommends = User.query.filter_by(recommend=True)
    return render_template('index.html', posts=posts, pagination=pagination, recommends=recommends)


# 上下文处理器，将变量暴露给所有模板
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


# 处理用户信息界面请求的路由
@main.route('/user/<username>')
def user(username):
    show_posts = True
    show_followed = False
    show_followers = False
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts, show_posts=show_posts, show_followers=show_followers,
                           show_followed=show_followed)


# 处理用户修改信息请求的路由
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('修改成功')
        return redirect(url_for('.user', username=current_user.username))
    form.username.data = current_user.username
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.about_me = form.about_me.data
        flash('修改成功')
        return redirect(url_for('.user', username=user.username))
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/write_articles', methods=['GET', 'POST'])
@login_required
def write_articles():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(title=form.title.data, outline=form.outline.data, body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    return render_template('write_articles.html', form=form)


# 显示文章详情的路由
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    praised = False
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          disabled=False,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('你的评论已提交')
        return redirect(url_for('.post', id=post.id))
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.filter_by(disabled=False).order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False
    )
    comments = pagination.items
    if current_user.is_anonymous:
        praised = True
    elif post.praised_by_users.filter_by(id=current_user.id).first():
        praised = True
    return render_template('post.html', post=post, form=form, comments=comments, pagination=pagination, praised=praised)


# 修改文章的路由
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTRATOR):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.outline = form.outline.data
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.outline.data = post.outline
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


# 用户关注相关的路由
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('你已经关注此用户')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('关注成功')
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('你尚未关注此用户')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('取关成功')
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    show_posts = False
    show_followers = False
    show_followed = True
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('user.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows, show_posts=show_posts, show_followers=show_followers,
                           show_followed=show_followed)


@main.route('/followed-by/<username>')
def followed_by(username):
    show_posts = False
    show_followers = True
    show_followed = False
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('user.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows, show_posts=show_posts, show_followers=show_followers,
                           show_followed=show_followed)


# 将评论置为不可用的路由
@main.route('/delete_comment/<int:post_id>/<int:comment_id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def delete_comment(post_id, comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.post', id=post_id))


@main.route('/recommend/<int:id>')
@login_required
@permission_required(Permission.ADMINISTRATOR)
def recommend(id):
    user = User.query.get_or_404(id)
    user.recommend = True
    db.session.add(user)
    return redirect(url_for('.user', username=user.username))


@main.route('/delete_recommend/<int:id>')
@login_required
@permission_required(Permission.ADMINISTRATOR)
def delete_recommend(id):
    user = User.query.get_or_404(id)
    user.recommend = False
    db.session.add(user)
    return redirect(url_for('.user', username=user.username))


@main.route('/praise/')
@login_required
def praise():
    id = request.args.get('post_id')
    post = Post.query.get_or_404(id)
    post_author = post.author
    if post.praised_by_users.filter_by(id=current_user.id).first():
        return jsonify({'praised': False})
    post.praise += 1
    post_author.likes += 1
    post.praised_by_users.append(current_user._get_current_object())
    db.session.add(post)
    return jsonify({'praised': True})


@main.route('/search', methods=['GET', 'POST'])
def search():
    data = request.form.get('keywords')
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter(Post.title.like('%' + data + '%')).order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POST_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    recommends = User.query.filter_by(recommend=True)
    return render_template('index.html', posts=posts, pagination=pagination, recommends=recommends)