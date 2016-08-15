import os
import MySQLdb
import xlrd

def findBoundingBoxByName(name):
	db = MySQLdb.connect("localhost","root","ncsu","glaciers")
#	print "Connection Established"
	cursor = db.cursor()
#	print "Cursor created"
	sql_query = 'select right_top_x,right_top_y,left_bottom_x,left_bottom_y from (select * from glaciers where glacier_name like "'+ name +'%") as t ORDER BY area DESC LIMIT 1;'

#	print sql_query
	try:
		cursor.execute(sql_query)
		r = cursor.fetchone()
	except MySQLdb.Error as e:
		print e.args[0],e.args[1]
		print "Error in fetching data"
	db.close()
	return (r[0],r[1],r[2],r[3])

def findStartByName(name):
	db = MySQLdb.connect("localhost","root","ncsu","glaciers")
#	print "Connection Established"
	cursor = db.cursor()
#	print "Cursor created"
	sql_query = 'select location_x,location_y from (select * from glaciers where glacier_name like "'+ name +'%") as t ORDER BY area DESC LIMIT 1;'
	try:
		cursor.execute(sql_query)
		r = cursor.fetchone()
	except MySQLdb.Error as e:
		print e.args[0],e.args[1]
		print "Error in fetching data"
	db.close()
	return (r[0],r[1])

def findBoundingBoxById(gid):
	db = MySQLdb.connect("localhost","root","ncsu","glaciers")
#	print "Connection Established"
	cursor = db.cursor()
#	print "Cursor created"
	sql_query = 'select right_top_x,right_top_y,left_bottom_x,left_bottom_y from glaciers where glacier_id="%s";' % gid
	try:
		cursor.execute(sql_query)
		r = cursor.fetchone()
	except:
		print "Error in fetching data"
	db.close()
	return (r[0],r[1],r[2],r[3])

def findStartById(gid):
	db = MySQLdb.connect("localhost","root","ncsu","glaciers")
#	print "Connection Established"
	cursor = db.cursor()
#	print "Cursor created"
	sql_query = 'select location_x,location_y from glaciers where glacier_id="%s";' % gid
	try:
		cursor.execute(sql_query)
		r = cursor.fetchone()
	except:
		print "Error in fetching data"
	db.close()
	return (r[0],r[1])

def findGroundMeasurement(glacier):
	db = MySQLdb.connect("localhost","root","ncsu","glaciers")
#	print "Connection Established"
	cursor = db.cursor()
#	print "Cursor created"
	sql_query = 'select year, front_variation from front_variation where glacier_name = (select wgms_name from commonDB where glims_name like "'+glacier+'%");' 
	try:
		cursor.execute(sql_query)
		rows = cursor.fetchall()
	except:
		print "Error in fetching data"
		return None
	db.close()
	return (rows)	
