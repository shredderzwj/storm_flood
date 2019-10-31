# -*- coding:utf-8 -*-

from flask import Flask, url_for, render_template, request, session, redirect
from functools import wraps
import hashlib

from cores.chart import get_area, get_chart, get_alphas, get_m, get_mu, get_pas
from cores.calc import Calculator
from cores.db_info import area_info


app = Flask(__name__)
app.secret_key = '23@#@34232DA4r2@#%33rdfRQd34@$@R#fqa23qf232@#%323r'
user = 'admin'
pwd = '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'


def check_login(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session.get('user') == user and session.get('pwd') == pwd:
			return f(*args, **kwargs)
		else:
			session['current_page'] = request.url
			# print(session['current_page'])
			return redirect(url_for('login'))
	return wrap


@app.route('/login', methods=["POST", "GET"])
def login():
	if request.method == 'POST':
		user_get = request.form['user']
		pwd_get = request.form['pwd']
		pwd_hash = hashlib.sha256(pwd_get.encode()).hexdigest()
		if user == user_get and pwd == pwd_hash:
			session['user'] = user
			session['pwd'] = pwd_hash
			return redirect(session.get('current_page') or url_for('frame'))
		else:
			return redirect(request.url)
	else:
		if session.get('user') == user and session.get('pwd') == pwd:
			return redirect(url_for('frame'))
		return render_template('login.html')


@app.route('/logout')
def logout():
	session['user'] = ""
	session['pwd'] = ""
	return redirect(url_for('login'))


@app.route('/')
def frame():
	return render_template('frame.html')


@app.route('/index')
def index():
	session['all_ps'] = [2, 20, 3, 30, 4, 40, 5, 50, 10, 100]  # 设计频率列表
	session['k'] = 3.5  # Cs/Cv
	session['imaxs'] = [50, 45, 40, 50, 55, 60]
	coord = request.args.get('coord')
	check = check_coord(coord)
	warning = ""
	if isinstance(check, str):
		warning = check
		coord = ''

	flood_info = {
		'warning': warning,
		'coord': coord,
		**session,
	}
	for k, v in flood_info.items():
		if not v:
			flood_info[k] = ""
	return render_template('index.html', **flood_info)


@app.route('/pick')
def pick_coord():
	return render_template('picker.html')


@app.route('/chart')
@check_login
def chart():
	coord = request.args.get('coord')
	for k, v in request.args.items():
		if k != 'coord':
			session[k] = float(v)

	check = check_coord(coord)
	if isinstance(check, tuple):
		lon, lat = check
		session['lon'] = lon
		session['lat'] = lat
		session['imax'] = ''
		chart_info = get_chart(lon, lat)
		# for k, v in chart_info.items():
		# 	session[k] = v
		area = chart_info['area']
		if 'area' in session:
			del session['area']
		if area < 7:
			imax = session['imaxs'][area - 1]
			session['imax'] = imax
			session['alphas'] = get_alphas(area, session['f'])
			session['theta'] = session['l'] / session['j'] ** (1 / 3) / session['f'] ** 0.25
			session['m'] = get_m(area, session['theta'])
			session['mu'] = get_mu(area)

		return render_template('chart.html', **chart_info, **session)
	else:
		warning = check
	# print(session)
	# if session.get('lon'):
	# 	return render_template('chart.html', **view.chart(session['lon'], session['lat']), **session, warning=warning)
	return render_template('index.html', **session, warning=warning)


@app.route('/result')
@check_login
def result():
	for k, v in request.args.items():
		if k == 'area':
			session[k] = int(v)
		else:
			session[k] = float(v)
	ps = []
	session['ps_var'] = []

	# 获取计算频率列表
	for p_var in request.args.keys():
		if p_var.startswith('p_'):
			p = 1 / float(p_var.split('_')[-1])
			ps.append(p)
			ps.sort(reverse=True)
			session['ps_var'].append(p_var)
	session['ps'] = ps
	if not ps:
		warning = '请选择计算频率！'
		del session['area']
		return render_template('chart.html', **get_chart(session['lon'], session['lat']), **session, warning=warning)

	# 获取4各点雨量列表
	yls = []
	for i in range(4):
		yls.append(session['yl_%d' % (i + 1)])
	session['yls'] = yls

	# 获取4各点雨量Cv列表
	cvs = []
	for i in range(4):
		cvs.append(session['cv_%d' % (i + 1)])
	session['cvs'] = cvs

	# 获取4各点雨量Cs列表
	session['css'] = [session['k'] * cv for cv in cvs]

	# 获取4各点面系数α列表
	alphas = []
	for i in range(4):
		alphas.append(session['alpha_%d' % i])
	session['alphas'] = alphas

	c = Calculator(**session)
	# for attr in dir(c):
	# 	if not attr.startswith('__'):
	# 		session[attr] = getattr(c, attr)
	# print(session)
	return render_template(
		'result.html', **session,
		ns=c.ns, r24ps=c.r24ps, kps=c.kps, design_point_rainfalls=c.design_point_rainfalls,
		design_area_rainfalls=c.design_area_rainfalls, r_24h_allocate=c.r_24h_allocate, qs=c.qs,
		pas=get_pas(ps, session['imax']), area_name=area_info[session['area']],
	)


@app.route('/image')
def get_image():
	key = request.args.get('key')
	file = url_for('static', filename='tu/%s.jpg' % key)
	return render_template('image.html', file=file)


@app.route('/show-doc-images')
def show_doc_images():
	return render_template('doc_images.html', image_num=range(1, 21))


@app.route('/clear-history')
def clear_history():
	keys = list(session.keys())[:]
	for k in keys:
		del session[k]
	return redirect(url_for('frame'))


def check_coord(coord):
	if coord:
		try:
			coord = coord.replace('，', ',')
			coord = coord.replace(' ', ',')
			coord = coord.replace('|', ',')
			lon, lat = [float(x) for x in coord.split(',')]
			area = get_area(lon, lat)
			if not area:
				return '省外坐标点！'
			# if area > 6:
			# 	return "山丘区以外坐标点"
		except Exception:
			return '无效坐标点！'
	else:
		return ""
	return lon, lat


if __name__ == '__main__':
	#app.run(debug=True, host='0.0.0.0')
	app.run()
