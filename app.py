# Mengimport library Web-flask
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

# Untuk mengcasting tipe data menjadi object id
from bson import ObjectId

# Helper Function
from utils.datetime_utils import *
from utils.db_class import *
from utils.db_query import *
from utils.dir import *
from utils.admin_manager import *
from utils.json import *
import os

# Menyetel konfigurasi app flask
app= Flask(__name__)

app.config['MONGODB_SETTINGS']= {
    'host': 'mongodb://localhost/test_news'
}

app.config['SECRET_KEY'] = 'kelompok 8 kelas A sistem basis data 2'

# Menginisialisasikan konstan
NEWS_IMAGE_DIR = 'img/news_image/'
PROFILE_PICTURE_DIR = 'img/profile_picture/'
NO_NEWS_IMAGE_PATH= 'default.JPG'
NO_PROFILE_PICTURE_PATH= 'no-profile-pic.jpg'

NEWS_PER_PAGE= 6

db= set_db(app)

# Halaman home
@app.route('/')
@app.route('/home/')
def home():
	# Mendapatkan seberapa banyak berita yang ada di database
	news_num= get_news_length()
	# Menyetel jumlah pagination
	pagination_num= news_num//NEWS_PER_PAGE if news_num%NEWS_PER_PAGE==0 else (news_num//NEWS_PER_PAGE) + 1

	# Mendapatkan nilai page di url
	page= request.args.get('page')
	# Jika page tidak diisi maka setel menjadi 1
	page= 1 if page is None else int(page)
	# Menghandle jika nilai page tidak valid
	if (page<1 or page>pagination_num):
		return redirect(url_for('home'))

	# Mendapatkan berita terbaru
	latest_news= get_latest_news(page, NEWS_PER_PAGE)
	# Mendapatkan berita terpopuler
	most_popular_news= get_most_popular_news(NEWS_PER_PAGE)
	# Mendapatkan list kategori yang ada di database
	category_list = enumerate(get_all_categories())

	# Mendapatkan tanggal hari ini
	curr_date= get_todays_day()+', '+get_convenience_date_format()

	# Mendapatkan top 10 tags
	highest_tags= get_top_n_tags(10)

	return render_template('user/home.html', latest_news=latest_news, page= page, news_per_pagination= NEWS_PER_PAGE, pagination_num= pagination_num, most_popular_news= most_popular_news, category_list= category_list, curr_date= curr_date, highest_tags= highest_tags, image_path= NEWS_IMAGE_DIR, no_image_path= NO_NEWS_IMAGE_PATH)


@app.route('/read/<news_id>')
def read_news(news_id=None):
	if(news_id is None):
		return redirect(url_for('home'))
        
        # Mendapatkan berita yang dipilih berdasarkan id yang dipass di route
	selected_data= get_news_by_id(news_id)
	# Meng-update jumlah baca berita yang dipilih
	selected_data.update(read_count=selected_data.read_count + 1)
	# Mendapatkan kategori dan penulis dari berita yang terpilih
	category= get_category_by_id(selected_data.category)
	writer= get_writer_by_id(selected_data.writer)
	# Melakukan operasi string split berdasarkan baris baru pada berita yang terpilih
	content_list= selected_data.content.split('\n')
	
	# Mendapatkan 5 berita terakhir diupload
	latest_news= get_latest_news(limit=5)
	
	# Mendapatkan hari apa saat ini
	todays_day= get_todays_day()
	# Mendapatkan tanggal saat ini dengan format yang telah ditentukan
	todays_date= get_convenience_date_format()

	return render_template('user/news_detail.html', selected_data= selected_data, category= category, writer= writer, content_list= content_list, latest_news= latest_news, todays_day= todays_day, todays_date= todays_date, image_path= NEWS_IMAGE_DIR, profile_path= PROFILE_PICTURE_DIR, no_image_path= NO_NEWS_IMAGE_PATH)


@app.route('/sort-by/<type>')
def sort_by(type=None):
	# Jika type yang di-pass type yang valid
	if(type in ['category', 'month_and_year', 'tags'] and type is not None):
		# Mendapatkan data yang digrup berdasarkan setiap type (kategori, bulan dan tahun atau tags)
		# Mendapatkan list type
		selected_data, sorted_by= get_sort_by(type)
		
		# Mendapatkan list semua tags dan kategori
		tag_list= get_all_tags()
		category_list = enumerate(get_all_categories())
		
		# Mendefinisikan prefix header dari halaman
		header_prefix= 'News sorted by '

		return render_template('user/sort_by.html', selected_data= selected_data, sorted_by= sorted_by, type=type, header_prefix= header_prefix, category_list= category_list, tag_list= tag_list, image_path= NEWS_IMAGE_DIR, no_image_path= NO_NEWS_IMAGE_PATH)
	else:
		return redirect(url_for('home'))


@app.route('/news-with/<type>/<sub_type>')
def news_with(type=None, sub_type=None):
        # Mengecek jika type dan sub type yang dipass valid
	if((type=='category' or type=='tags') and (type is not None and sub_type is not None)):
		try:
			selected_data, sorted_by= get_news_with(type, sub_type)
			tag_list= get_all_tags()
			category_list = enumerate(get_all_categories())
			header_prefix= 'News with '

			return render_template('user/sort_by.html', selected_data=selected_data, sorted_by=sorted_by, type=type, header_prefix= header_prefix,  category_list= category_list, tag_list= tag_list, image_path=NEWS_IMAGE_DIR, no_image_path= NO_NEWS_IMAGE_PATH)
		except:
			flash(('Invalid url end point'), 'danger')
			return redirect(url_for('home'))
	else:
		flash(('Invalid url end point'), 'danger')
		return redirect(url_for('home'))


@app.route('/login/', methods=['GET', 'POST'])
@guess_required
def login():
	if request.method=='POST':
		username= request.form['username']
		password= request.form['password'] # Hash this later

		if(check_user(username, password)):
			user= get_writer_by_username(username)
			session['user_id']= str(ObjectId(user.pk))

			return redirect(url_for('admin_dashboard'))
		else:
			flash(('Invalid username or password'), 'danger')
			return redirect(url_for('login'))

	return render_template('user/login.html')


@app.route('/logout/', methods=['GET', 'POST'])
@login_required
def logout():
	session.pop('user_id', None)
	return redirect(url_for('home'))


@app.route('/admin-dashboard/')
@login_required
def admin_dashboard():
	user= current_user()
	is_admin= logged_user_is_admin()
	return render_template('admin/admin_dashboard.html', user= user, is_admin= is_admin, no_profile_picture_path= NO_PROFILE_PICTURE_PATH, image_path=PROFILE_PICTURE_DIR)


@app.route('/manage-categories/')
@login_required
@admin_required
def manage_categories():
	categories= get_all_categories()

	if(len(categories)>0):
		num_of_news_list = [len(get_news_by_category(i)) for i in categories]
		categories= enumerate(categories)
	else:
		num_of_news_list = []
		categories= enumerate([])

	global NEWS_IMAGE_DIR

	return render_template('admin/manage_category.html', categories= categories, num_of_news_list= num_of_news_list, image_path= NEWS_IMAGE_DIR)


@app.route('/input-category/', methods=['GET', 'POST'])
@login_required
@admin_required
def input_category():
	category_list= get_all_categories()

	return render_template('admin/input_category.html', category_list=category_list)


@app.route('/inserting-category/', methods=['GET', 'POST'])
@login_required
@admin_required
def inserting_category():
	category_list= get_all_categories()

	if request.method=='POST':
		category= request.form['category']

		if category in [i.category for i in category_list]:
			flash(('The entered category already exists in the database'), 'danger')
			return redirect(url_for('input_category'))

		insert_category = Categories(category=category)
		insert_category.save()

		flash(('Successfully added new category'), 'success')

	return redirect(url_for('manage_categories'))


@app.route('/deleting-category/<category_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def deleting_category(category_id=None):
	if category_id is not None:
		delete_category= get_category_by_id(category_id)

		if (len(get_news_by_category(delete_category))>0):
			flash(('Deletion failed, there is still news with the relevant category'), 'danger')
		else:
			flash(('Successfully deleted'), 'success')
			delete_category.delete()

	return redirect(url_for('manage_categories'))


@app.route('/manage-news/')
@login_required
def manage_news():
	writer= current_user()

	news= get_all_news() if logged_user_is_admin() else get_news_by_writer(writer)
	if(len(news)>0):
		writer = get_writer_by_news(news)
		categories= get_categories_by_news(news)
		news= enumerate(news)
	else:
		writer= []
		categories= []
		news= enumerate([])

	return render_template('admin/manage_news.html', news= news, writer= writer, categories= categories, image_path= NEWS_IMAGE_DIR, no_image_path= NO_NEWS_IMAGE_PATH)


@app.route('/input-news/', methods=['GET', 'POST'])
@login_required
def input_news():
	possible_categories= get_all_categories()
	submit_type= 'input_news'

	return render_template('admin/input_news.html', possible_categories=possible_categories, submit_type= submit_type)


@app.route('/inserting-news/', methods=['POST'])
@login_required
def inserting_news():
	if request.method=='POST':
		file = request.files['file']
		if file.filename == '':
			filename= ''

		else:
			filename = secure_filename(file.filename)
			if(filename in get_news_image_path_list()):
				filename= handle_duplicate_img_filename(filename)

			filepath = os.path.join(('static/'+NEWS_IMAGE_DIR), filename)
			file.save(filepath)

		title= request.form['title']
		category= get_category_by_category(request.form['category']).pk
		uploaded_date= request.form['uploaded_date']
		tags= map(str.strip, request.form['tags'].split(','))
		writer= ObjectId(session.get('user_id'))
		content= request.form['content']
		read_count= 0

		insert_news = News(
			title=title, category=category, uploaded_date=uploaded_date, tags=tags,
			writer=writer, img_path=filename, read_count=read_count, content=content
		)
		insert_news.save()
		flash(('Successfully added new news'), 'success')

	return redirect(url_for('manage_news'))


@app.route('/update-news/<news_id>', methods=['GET', 'POST'])
@login_required
def update_news(news_id=None):
	if news_id is None:
		return redirect(url_for('home'))

	selected_data = get_news_by_id(news_id)

	if(logged_user_is_admin() or logged_user_is_user(selected_data.writer)):
		selected_category= get_category_by_id(selected_data.category).category
		possible_categories= get_all_categories()
		submit_type= 'update_news'

		global NEWS_IMAGE_DIR

		return render_template('admin/input_news.html', possible_categories=possible_categories, submit_type= submit_type, selected_data=selected_data, selected_category= selected_category, image_path= NEWS_IMAGE_DIR)
	else:
		flash(('You have no permissions to access this page'), 'danger')
		return redirect(url_for('manage_news'))


@app.route('/updating-news/<news_id>', methods=['POST'])
@login_required
def updating_news(news_id=None):
	if news_id is None:
		return redirect(url_for('home'))

	if request.method=='POST':
		update_news = get_news_by_id(news_id)
		if (logged_user_is_admin() or logged_user_is_user(update_news.writer)):
			file = request.files['file']
			if file.filename == '':
				file.filename= update_news.img_path
				filename = secure_filename(file.filename)

			else:
				delete_image_of(update_news.img_path, folder_location= NEWS_IMAGE_DIR)

				filename = secure_filename(file.filename)
				if (filename in get_news_image_path_list()):
					filename = handle_duplicate_img_filename(filename)

				filepath = os.path.join(('static/'+NEWS_IMAGE_DIR), filename)
				file.save(filepath)

			title= request.form['title']
			category= get_category_by_category(request.form['category']).id
			uploaded_date= request.form['uploaded_date']
			tags= map(str.strip, request.form['tags'].split(','))
			content= request.form['content']

			update_news.update(
				title= title, category= category, uploaded_date= uploaded_date,
				tags= tags, img_path= filename, content= content
			)

			flash(('Updated successfully'), 'success')

	return redirect(url_for('manage_news'))


@app.route('/deleting-news/<news_id>')
@login_required
def deleting_news(news_id=None):
	if news_id is not None:
		delete_news = get_news_by_id(news_id)
		if (logged_user_is_admin() or logged_user_is_user(delete_news.writer)):
			if delete_news.img_path!='':
				delete_image_of(delete_news.img_path, folder_location= NEWS_IMAGE_DIR)

			delete_news.delete()
			flash(('Successfully deleted'), 'success')
		else:
			flash(('You have no permissions to access this page'), 'danger')

	return redirect(url_for('manage_news'))


@app.route('/manage-users/')
@login_required
@admin_required
def manage_users():
	users = get_all_writers()
	num_of_users_list = [len(get_news_by_writer(i)) for i in users]
	users= enumerate(users)

	return render_template('admin/manage_users.html', users= users, num_of_users_list= num_of_users_list, image_path= PROFILE_PICTURE_DIR, no_profile_picture_path= NO_PROFILE_PICTURE_PATH)


@app.route('/input-user/', methods=['GET', 'POST'])
@login_required
@admin_required
def input_user():
	submit_type= 'input_user'
	return render_template('admin/input_user.html', submit_type= submit_type, image_path= PROFILE_PICTURE_DIR, no_profile_picture_path= NO_PROFILE_PICTURE_PATH)


@app.route('/inserting-user/', methods=['POST'])
@login_required
@admin_required
def inserting_user():
	if request.method=='POST':
		file = request.files['file']
		if file.filename == '':
			filename = ''
		else:
			filename = secure_filename(file.filename)
			if(filename in get_news_image_path_list()):
				filename= handle_duplicate_img_filename(filename)

			filepath = os.path.join(('static/'+PROFILE_PICTURE_DIR), filename)
			file.save(filepath)

		username= request.form['username']
		password= request.form['password']
		authority= request.form['authority']

		insert_user= Writer(username= username, password= password, authority= authority, profile_pict_path= filename)
		insert_user.save()

		flash(('User added successfully'), 'success')

	return redirect(url_for('manage_users'))


@app.route('/update-user/<user_id>', methods=['GET', 'POST'])
@login_required
def update_user(user_id=None):
	if user_id is not None :
		selected_user = get_writer_by_id(user_id)
		if (logged_user_is_admin() or logged_user_is_user(selected_user.pk)):
			submit_type= 'update_user'

			return render_template('admin/input_user.html', selected_user=selected_user, submit_type= submit_type, image_path= PROFILE_PICTURE_DIR, no_profile_picture_path= NO_PROFILE_PICTURE_PATH)
		else:
			flash(('You have no permissions to access this page'), 'danger')

	return redirect(url_for('admin_dashboard'))

@app.route('/updating-user/<user_id>', methods=['POST'])
@login_required
def updating_user(user_id=None):
	if (request.method=='POST' and user_id is not None):
		update_user = get_writer_by_id(user_id)
		if (logged_user_is_admin() or logged_user_is_user(update_user.pk)):
			file = request.files['file']
			if file.filename == '':
				file.filename = update_user.profile_pict_path
				filename = secure_filename(file.filename)
			else:
				delete_image_of(update_user.profile_pict_path, folder_location=PROFILE_PICTURE_DIR)

				filename = secure_filename(file.filename)
				if (filename in get_news_image_path_list()):
					filename = handle_duplicate_img_filename(filename)

				filepath = os.path.join(('static/' + PROFILE_PICTURE_DIR), filename)
				file.save(filepath)

			username= request.form['username']
			password= request.form['password']
			authority= request.form['authority']

			update_user.update(username= username, password= password, authority= authority, profile_pict_path= filename)

			flash(('Updated Successfully'), 'success')

	return redirect(url_for('manage_users'))


@app.route('/deleting-user/<user_id>')
@login_required
@admin_required
def deleting_user(user_id=None):
	if user_id is not None:
		delete_user = get_writer_by_id(user_id)
		if (len(get_news_by_writer(delete_user)) > 0):
			flash(('Deletion failed, there is still news with the relevant writer'), 'danger')
			pass
		else:
			if delete_user.profile_pict_path != '':
				delete_image_of(delete_user.profile_pict_path, folder_location=PROFILE_PICTURE_DIR)

			delete_user.delete()
			flash(('Successfully deleted'), 'success')

	return redirect(url_for('manage_users'))


@app.context_processor
def context_processor():
	return dict(is_logged_in= is_logged_in())


if(__name__=="__main__"):
	app.run(debug=True)
