'''
Created on Jun 2, 2015

@author: User
'''
import json

from jsonrpc import ServerProxy, JsonRpc20, TransportTcpIp, \
    RPCInternalError


class Parser(object):
    '''
    classdocs
    '''

    def __init__(self, host = '127.0.0.1', begin_value = 2346, t = 10):
        '''
        Constructor
        '''
        ports = []
        for i in xrange(t):
            ports.append(begin_value + i)
        
        self.servers = []
        for i in xrange(t):
            port = begin_value + i
            self.servers.append(ServerProxy(JsonRpc20(),
                                  TransportTcpIp(addr=("127.0.0.1", port), timeout=50.0)))
        self.no_of_servers = len(self.servers)
        
    def parse(self, index, text):
        return json.loads(self.servers[index].parse(text))
    
    def parse_tolerant(self, index, text):
        try:
            parsed = self.parse(index, text)
            return parsed
        except RPCInternalError:
            print '----------------Unparsedable-----------------'
            print text
            return None
        except:
            print '----------------Other problem-----------------'
            print text
            return None