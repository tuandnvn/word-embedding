'''
Created on Jun 2, 2015

@author: User
'''

if __name__ == '__main__':
    ports = []
    
    for port in ports:
        server = jsonrpc.Server(jsonrpc.JsonRpc20(),
                                    jsonrpc.TransportTcpIp(addr=('127.0.0.1', port)))
            
        nlp = StanfordCoreNLP()
        server.register_function(nlp.parse)
        
        print 'Serving on http://%s:%s' % ('127.0.0.1', port)
        server.serve()