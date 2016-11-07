from pylxd import  Client
import json
'''
-------------------------------------------
    Class: Loads the Configuration class
----------------------------------------------
'''
class Config:
    server_config=None;
    cp_config=None;
    
    @staticmethod
    def init():
        Config.loadCpJson();
        Config.loadServerJson();        
        
    @staticmethod     
    def loadCpJson():
        cp_file=open("cp.config","r")
        Config.cp_config=json.load(cp_file);        

    @staticmethod     
    def loadServerJson():
        s_file=open("server.config","r");
        Config.server_config=json.load(s_file);        


'''
-------------------------------------------
    Class: Class obj will info about the server
----------------------------------------------
'''

class ServerBO:
    '''
    -------------------------------------------
        Desc: Constructor
    ----------------------------------------------
    '''
    def __init__(self,_host,_uri):
        self.host=_host;
        self.uri=_uri;
        self.client=self.creatClient();

    '''
    -------------------------------------------
        Desc: Creates the lxd client obj
        return : Obj is successfull else None
    ----------------------------------------------
    '''        
    def creatClient(self):
        client= Client(endpoint=self.uri, cert=(Config.cp_config["cert"],Config.cp_config["key"]),verify=False);
        client.authenticate(Config.cp_config["trustPassword"]);
        if(client.trusted):
            return client;
        else:
            return None;

'''
-------------------------------------------
    Class: Class obj will info about the server
----------------------------------------------
'''
class ContainerBO:
    '''
    -------------------------------------------
        Desc: Constructor
    ----------------------------------------------
    '''
    def __init__(self):
        self.cpu=None;
        self.memory=None;
        self.container=None;
        self.isRunning=(lambda: True if self.container.status=="Running" else False);

    '''
    -------------------------------------------
        Desc: gets the Cpu Limit
    ----------------------------------------------
    '''    
    def getCpuLimit(self):
        if self.container == None:
            return None;
        cpu=self.container.config.get("limits.cpu");        
        return cpu if cpu!=None and len(cpu)>0 else None;

    '''
    -------------------------------------------
        Desc: gets the mem Limit
    ----------------------------------------------
    '''   
    def getMemoryLimit(self):
        if self.container == None:
            return None;
        mem=self.container.config.get("limits.memory");
        return mem[:-2] if mem!=None and len(mem)>0 else None;
    '''
    -------------------------------------------
        Desc: get running status
    ----------------------------------------------
    '''   
    def getRunningStatus(self):
        if self.container == None or not self.isRunning():
            return None;
        status=self.container.execute(["vmstat","1","-n","5"])[0];
        lines=status.split("\n");
        frequency=0;
        cpu_usage=0;
        mem_usage=0;
        for lno in range(0,len(lines)):            
            if lno >1 and len(lines[lno])>0:                
                col=lines[lno].split();
                cpu_usage+=100-int(col[14]);
                mem_usage+=int(col[3]);
                #print(col[3]+" - "+col[14]);
                frequency+=1;
        avg_mem_usage=int(mem_usage/(frequency if frequency !=0 else 1));
        avg_cpu_usage=int(cpu_usage/(frequency if frequency !=0 else 1));
        return {"cpu":avg_cpu_usage,"mem":avg_mem_usage};