import datetime,totpGenerator,jwt
from functools import wraps
import saltAndHash,cv2 as cv
from flask import Flask, render_template, request,make_response,jsonify,session,Response,redirect,url_for
from flask_mysqldb import MySQL
import keys

#initializing the flask application
app = Flask(__name__)


#configuring the SQL database connection

app.config['MYSQL_USER']=keys.user
app.config['MYSQL_PASSWORD']=keys.password
app.config['MYSQL_HOST']=keys.host
app.config['MYSQL_DB']=keys.database_name
app.config['SECRET_KEY']=keys.secret_key

sql=MySQL(app)


#Checks the HTTP request header for a valid JWT token
def check_for_token(func):
    @wraps(func)
    def wrapped(*args,**kwargs):
        token=request.cookies['token']
        
        #User is redirected to the login page when no token in found
        if not token:
            return redirect(url_for('index'))
        
        #Validates the JWT token
        else:
        	try:
        		data=jwt.decode(token,app.config['SECRET_KEY'],algorithms="HS256")
        #Redirects the user to login page
        	except:
        		return redirect("/")   	
                
        return func(*args,**kwargs)
    return wrapped



#Unprotected endpoint - can be accessed without authentication
@app.route('/')
def index():
    return render_template('index.html')


#JWT protected endpoint(Can only be accessed after successful authentication) 
#Endpoint provides options to control all the appliances
@app.route('/smartHomeControl')
@check_for_token
def smartHomeControl():
    
    return render_template('controll.html')


#JWT protected endpoint(Can only be accessed after successful authentication) 
# Checks the current state of the lamp connected to the home network
@app.route('/status')
@check_for_token
def status_check():
    
    return Response(tableLamp.status())



#JWT protected endpoint(Can only be accessed after successful authentication) 
# Allows the users to view the live-stream data from an IP camera
@app.route('/camera')
@check_for_token
def camera():
    return render_template('camera.html')


#JWT protected endpoint(Can only be accessed after successful authentication) 
# Allows the users to turnOn the lamp connected to the home network
@app.route('/powerOn')
@check_for_token
def turnOn():
    return tableLamp.turnOn()


#JWT protected endpoint(Can only be accessed after successful authentication) 
#Allows the users to turnOff the lamp 
@app.route('/powerOff')
@check_for_token
def turnOff():
    return tableLamp.turnOff()



#JWT protected endpoint(Can only be accessed after successful authentication) 
# Gets the temperature and humidity information from the connected DHT sensor
@app.route('/temperature')
@check_for_token
def temperature():
    result = tempHumidity.readSensor()
    result[0] = round(result[0], 4)
    result[1] = round(result[1], 4)
    return render_template('temperature.html', result=result)



# Connectes to the IP camere and captures it's frames 
def gen():
    camera = cv.VideoCapture('http://192.168.0.100:4747/video')
    while True:

        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


#JWT protected endpoint(Can only be accessed after successful authentication) 
# Streams the captured frames to camera.html 
@app.route('/video')
@check_for_token
def video():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')





# Authenticates the user using the login creds and Time based OTP
@app.route('/login',methods=['POST'])
def login():
    username=request.form['username']
    password=request.form['password']
    otp=request.form['otp']

	#A database connection is initialized and the DB is queried for the given user info
    cur=sql.connection.cursor()
    cur.execute("SELECT password,totp from users where email=%s  OR name=%s",[username,username])
    result=cur.fetchall()
    secret_key=result[0][1]    # Secret_key for the given user(used for the creation/verfication of TOTP) is retrieved from the DB
    hash=result[0][0]          # Password hash for the given user is retrieved from DB 



	# Verifies the password and TOTP for it's correctness
    if saltAndHash.verifyPassword(password,hash) and totpGenerator.verifyOTP(secret_key,otp):
    
    # When the creds are verified to be correct then a JWT token is created and the token is added as a cookie in the server response
        
        session['logged_in']=True
        token=jwt.encode({"user":username,"exp":datetime.datetime.utcnow()+datetime.timedelta(minutes=5)},app.config['SECRET_KEY'])
        res=make_response(redirect('/smartHomeControl'))
        res.set_cookie('token',token,httponly=True)
        
        return res
        


   
    else:
        res=make_response("<h2> Sorry the credentials are invalid !!")
        
        return res


# Allows the new users to create their account
@app.route('/registration')
def redirection():
    return render_template('register.html')



#Creates a new user account in DB based on the provided user info
@app.route('/register',methods=['POST'])
def register():
	    #Collects user info from the HTTP request headers  
            username=request.form['username']
            password=request.form['password']
            email=request.form['email']
            
            # A DB connection is initialized and checks for the availability of the username
            cur = sql.connection.cursor()
            result=cur.execute("SELECT * FROM users where name=%s or email=%s",[username,email])
            
            # When user not present in DB ,a TOTP secret and password hash is created for the user and a new entry is made for that specific user 
            if result==0:
                secret=totpGenerator.generateTOTP()
                cur.execute("INSERT INTO users VALUES(%s,%s,%s,%s)",(username,saltAndHash.hashPassword(password),email,secret))
                sql.connection.commit()

# When the username is already taken, a username not available response is made
            else:
                return render_template('register.html',invalid_input="The username or email specified is already taken!! Please use different email or username")
            cur.close()
            
            # Confirms the user when the registration is successfull 
            return render_template('index.html',registration_successful="Account has been created successfully !! Please login with your credentials")



if __name__ == '__main__':
    app.run()
