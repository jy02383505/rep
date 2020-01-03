# import ConfigParser
#
#
# config = ConfigParser.RawConfigParser()
# config.read('/Application/rep/conf/rep.conf')
#
# def initConfig():
#     config = ConfigParser.RawConfigParser()
#     config.read('/Application/rep/conf/rep.conf')
#     return config


#import ConfigParser
import configparser

#config = ConfigParser.RawConfigParser()
#config = configparser.RawConfigParser()
config = configparser.ConfigParser()
config.read('/Application/rep/conf/rep.conf')

def initConfig():
    config = ConfigParser.RawConfigParser()
    config.read('/Application/rep/conf/rep.conf')
    return config