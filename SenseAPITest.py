import senseapi
import json

#####################
# I M P O R T A N T #
#####################
# This test script will attempt to open a file to read 
# credentials with which it will authenticate at 
# CommonSense. Make sure this file is present!
try:
    f = open('credentials.txt', 'r')
except:
    print 'pieuw'
creds = json.load(f)
f.close()
print creds

try:
    username = creds['username']
    password = creds['password']
except: 
    print 'session_id authentication not available!'
    username = ''
    password = ''
    
try:
    oauth_token_key         = str(creds['oauth_token_key'])
    oauth_token_secret      = str(creds['oauth_token_secret'])
    oauth_consumer_key      = str(creds['oauth_consumer_key'])
    oauth_consumer_secret   = str(creds['oauth_consumer_secret'])
except:
    print 'oauth authentication not available!'
    oauth_token_key         = ''
    oauth_token_secret      = ''
    oauth_consumer_key      = ''
    oauth_consumer_secret   = ''


# Set all things to be tested
AUTHENTICATE_SESSIONID      = True
AUTHENTICATE_OAUTH          = False

TEST_GETSENSORS             = False
TEST_GETSENSORDATA          = True
TEST_POSTSENSORS            = False
TEST_POSTSENSORDATA         = False
TEST_CREATESERVICE          = False
TEST_CREATENOTIFICATION     = False
TEST_OAUTHAUTHORIZATION     = False 
TEST_OAUTHAUTHENTICATION    = False

api = senseapi.SenseAPI()
api.setVerbosity(True)
api.setServer('live')

# login
if AUTHENTICATE_SESSIONID:
    password_md5 = senseapi.MD5Hash(password)
    status, response = api.AuthenticateSessionId(username, password_md5)
    print(response)

if AUTHENTICATE_OAUTH:
    status, response = api.AuthenticateOauth(oauth_token_key, oauth_token_secret, oauth_consumer_key, oauth_consumer_secret)

# get sensor list
if TEST_GETSENSORS:
    parameters = api.SensorsGet_Parameters()
    parameters['owned'] = 1
    parameters['physical'] = 1
    parameters['page'] = 0
    status, response = api.SensorsGet(parameters)
    print(response)

# get sensor data 
if TEST_GETSENSORDATA:
    parameters = api.SensorDataGet_Parameters()
    del parameters['date']
    del parameters['next']
    parameters['start_date'] = 1331215067
    parameters['end_date'] = 1331215667
    status, response = api.SensorDataGet(150776, parameters)
    print response

# post a sensor
if TEST_POSTSENSORS:
    parameters = api.SensorsPost_Parameters()
    parameters['sensor']['name'] = 'test_sensor'
    parameters['sensor']['device_type'] = 'gyrocopter'
    parameters['sensor']['data_type'] = 'float'
    status, response = api.SensorsPost(parameters)
    print response
    sensor_id = response['sensor']['id']
    
if TEST_POSTSENSORDATA:
    data = {'data':[{'value':10, 'date':1343055000},{'value':11, 'date':1343055001}]}
    status, response = api.SensorDataPost(sensor_id, data)
    print response

# post sensor data

# create a service for battery sensor
#parameters = api.ServicesPost_Parameters()
#parameters['service[data_fields]'] = ['level']
#parameters['sensor[name]'] = 'ChargeNeeded'
#parameters['sensor[device_type]'] = 'ChargeNeeded'
if TEST_CREATESERVICE:
    parameters = {'service':{'name':'math_service', 'data_fields':['level']}, 'sensor':{'name':'ChargeNeeded', 'device_type':'ChargeNeeded'}}
    status, response = api.ServicesPost(sensor_id, parameters)
    print response
    service_id = response['service[id]']
# setup the expression
    parameters = api.ServicesSetExpression_Parameters()
    parameters['parameters'] = ["_113522_battery_sensor.level"]
    status, response = api.ServicesSetExpression(sensor_id, service_id, parameters)
    print response
# add it to a device
    parameters = api.SensorAddToDevice_Parameters()
    parameters['device']['type'] = 'redXI'
    parameters['device']['uuid'] = 'bla:diebla'
    del parameters['device']['id']
    res, resp = api.SensorAddToDevice(service_id, parameters)

# create a notification for new sensors
if TEST_CREATENOTIFICATION:
    parameters = api.NotificationsPost_Parameters()
    parameters['notification']['type'] = 'url'
    parameters['notification']['text'] = 'herpaderping'
    parameters['notification']['destination'] = 'http://data.sense-os.nl:9012/scripts/ClimateSystemMap'
    status, response = api.NotificationsPost(parameters)
    print response
    notification_id = response['notification']['id']    
# setup the event
    status, parameters = api.EventsNotificationsPost_Parameters()
    parameters['event_notification']['name'] = 'new sensor event'
    parameters['event_notification']['event'] = 'add_sensor'
    parameters['event_notification']['notification_id'] = notification_id
    status, response = api.EventsNotificationsPost(parameters)
    print response

# test oauth authentication
if TEST_OAUTHAUTHORIZATION:
    result  = ''
    token   = {}
    if api.server == 'live':
        result, token = api.OauthAuthorizeApplication('ZDljODM4NTI4NTI4NzAzNDIzYjg', 'ZmI3NDJmNmM1ZjE3ZjZhMzgxMjI', 'for_ever')
    elif api.server =='dev':
        result, token = api.OauthAuthorizeApplication('NDQ1NTJjYTE0NjFkNmExYzI0Njc', 'OTA3NDg3ODRmNGZhYzU4MmNkMWM', 'for_ever')
    print '-----------------------------'
    print result
    print token
    print '-----------------------------'
  
# get current user
if TEST_OAUTHAUTHENTICATION:
    result, response = api.UsersGetCurrent()
    print result, response
  
#    consumer = api.OauthGetConsumer('ZDljODM4NTI4NTI4NzAzNDIzYjg', 'ZmI3NDJmNmM1ZjE3ZjZhMzgxMjI')
#    response = api.OauthRequestToken(consumer)
#    print response
#    response = api.OauthAuthorize()
#    response = api.OauthAccessToken(consumer)
#    print response
#logout
if AUTHENTICATE_SESSIONID:
    status, response = api.Logout()
    print(response)