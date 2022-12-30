
from .calculations import Calc_COG_env, \
    Calc_load_dis,Calc_factors,Calc_rigging,Calc_SKL


class communicater_calculations:
    def __init__(self,params,**kwargs):
        # Getting the params:
        self.point_names=["A","B","C","D"]
        # General parameters
        self.N_lifts = params["N_lifts"] # Number of lifts
        self.Roll_bool = params["TEF_x_bool"]
        self.Pitch_bool = params["TEF_y_bool"]
        general_params= params.tab_1
        general_factor_params =   params.tab_2.section_1
        SSF_params = params.tab_2.section_2


        # making tef factor (kan worden verwijdert)

        tef_factor = []
        for i in range(self.N_lifts):
            tef_factor.append(1)

        # Getting data 
        self.data_general = self.make_data_general(general_params)

        self.data_SSF_factors = self.make_data_SSF_factor(
                                                SSF_params)
        self.data_general_factor = self.make_data_general_factor(
                                                general_factor_params)

        #print(self.data_rigging)
        # Print statements kan worden verwijdert
        #print(_Calc_factors)
        #print(self.data_cranes)
        #print(self.data_general)
        #print(self.data_general_factor)
        #print(self.data_SSF_factors)
       

        # Calculations classes
        # Calculate COG envelope
        #print(self.data_general)
        _Calc_COG_env = Calc_COG_env(self.data_general["Obj_geo"],
                                         self.data_general["COG"])
        # Calculating the load dis
        _Calc_load_dis = Calc_load_dis(self.data_general["Lift_points"],
                                      _Calc_COG_env,
                                      self.data_general["COG"],
                                      self.N_lifts,
                                      self.data_general["LW"])
        _Calc_factors = Calc_factors(self.data_general_factor,
                                    _Calc_load_dis,
                                    self.data_general["LW"],
                                    self.data_SSF_factors,
                                    self.N_lifts,
                                    tef_factor)

        

                                    

        # Making attributes so it can be shared with the other method 
        self.Load_dis_perc = _Calc_load_dis.return_load_dis
        self.Load_dis_t = _Calc_load_dis.get_load_dis_tons
        self.factors = _Calc_factors.get_general_factors
        self.COG_shift = _Calc_load_dis.get_max_cog_shifts
        print(self.factors)

    def make_data_skl(self,params):
        Data_SKl ={}
        Data_SKl["Hook_point"] = [params["Hook_x"]*1000,
                                  params["Hook_y"]*1000,
                                  params["Hook_z"]*1000]
        Data_SKl["Lift_points"]=[]
        lift_points_table = params.table_lift_points_skl
        for i in range(4):
            point =[0,0,0]
            point[0]= lift_points_table[i]["x"]*1000
            point[1]= lift_points_table[i]["y"]*1000
            point[2]= lift_points_table[i]["z"]*1000
            Data_SKl["Lift_points"].append(point)
        
        Data_SKl["Lslings"]=[]
        Data_SKl["Eslings"]=[]
        Data_SKl["Dslings"]=[]

        table_slings = params.table_slings
        for i in range(4):
            Data_SKl["Lslings"].append(table_slings[i]["Length"])
            Data_SKl["Eslings"].append(table_slings[i]["E_modulus"])
            Data_SKl["Dslings"].append(table_slings[i]["D_slings"])
            
        # Checks kan worden verwijdert
        for i in range(4):
            Hook_point=Data_SKl["Hook_point"]
            Lift_point=Data_SKl["Lift_points"][i]
            #L=cal.distance_points_3d(Hook_point,Lift_point)
            #print("Sling "+str(i+1)+": "+str(L))
        return Data_SKl

    def make_data_SSF_factor(self, params):
        Data_SSF_factor = []
        dynamic_array_SSF = params.SSF_data
        # name of keys 
        for row in dynamic_array_SSF:
            SSF_data = {}
            if row["lift_factor_bool"] == False:
                SSF_data["Lift_factor"] = 1.3
            else:
                SSF_data["Lift_factor"] = row["lift_factor"]
            
            if row["consequence_factor_bool"] == False:
                SSF_data["Consequence_factor"] = 1.3
            else:
                SSF_data["Consequence_factor"] = row["consequence_factor"]
            SSF_data["Material_factor"]=row['Material_factor']
            SSF_data["Wear_application_factor"]=row['Wear_application_factor']
            Data_SSF_factor.append(SSF_data)
    
        return Data_SSF_factor

   

    def make_data_general_factor(self,params):
        Data_general_factor = {}
        keys = ["WCF", "COGCrane", "DAF","COG_envelope","YAW"]
        for key in keys:
            Data_general_factor[key] = params[key]
        Data_general_factor["TEF"] = [0,0]
        if self.Roll_bool == True:
            Roll_angle = params['tilt_factor_x_axes_angle']
            Data_general_factor["TEF"][0] = Roll_angle
        else:
            Data_general_factor["TEF"][0] = 0
        
        if self.Pitch_bool == True:
            Pitch_angle = params['tilt_factor_y_axes_angle']
            Data_general_factor["TEF"][1] = Pitch_angle
        else:
            Data_general_factor["TEF"][1] = 0
        #print(Data_general_factor)
        
        return Data_general_factor

    def make_data_general(self,params):
        Data_general={}
        # Storing lift points coardinates
        lift_points_table = params.section_1.Lift_points_table
        Data_general["Lift_points"] = []
        for i in range(self.N_lifts):
            point=[0, 0, 0]
            point[0] = lift_points_table[i]["x"]*1000
            point[1] = lift_points_table[i]["y"]*1000
            point[2] = lift_points_table[i]["z"]*1000
            Data_general["Lift_points"].append(point)

        # Storing object geometry
        length = params.section_2["Object_x"]*1000
        width = params.section_2["Object_y"]*1000
        height = params.section_2["Object_z"]*1000
        Data_general["Obj_geo"]= [0,0,0]
        Data_general["Obj_geo"][0] = length
        Data_general["Obj_geo"][1] = width
        Data_general["Obj_geo"][2] = height

        # Storing COG values 
        Data_general["COG"] = [0,0,0]
        Data_general["COG"][0] = params.section_1["COG_x"]*1000
        Data_general["COG"][1] = params.section_1["COG_y"]*1000
        Data_general["COG"][2] = params.section_1["COG_z"]*1000

        # Storing weight
        Data_general["LW"] = params.section_3["LW"]

        return Data_general

    def make_data_cranes(self, params):
        
        # info crane 1:
        info_crane_1 = {}
        params_crane_1 = params.section_2.table_crane1
        info_crane_1["name"] = params.section_2["Crane_name"]
        info_crane_1["DDF"] = params.section_2["DDF"]
        for i in range(3):
            hoist = params_crane_1[i]["Hoist"]
            offlead = params_crane_1[i]["offlead"]
            Capacity = params_crane_1[i]["Capacity"]
            RW = params_crane_1[i]["RW"]
            info_crane_1[hoist] = [Capacity ,offlead ,RW]
        

        # info crane 2:
        info_crane_2 = {}
        params_crane_2 = params.section_3.table_crane2
        info_crane_2["name"] = params.section_3["Crane_name"]
        info_crane_2["DDF"] = params.section_3["DDF"]
        for i in range(3):
            hoist = params_crane_2[i]["Hoist"]
            offlead = params_crane_2[i]["offlead"]
            Capacity = params_crane_2[i]["Capacity"]
            RW = params_crane_2[i]["RW"]
            info_crane_2[hoist] = [Capacity ,offlead ,RW]
        
       
        Data_crane = {}
        lifted_by_table = params.section_1.Lifted_by_data
        for i in range(self.N_lifts):
            point=  lifted_by_table[i]["point"]
            
            Hoist = lifted_by_table[i]["hoist"]
            Crane = lifted_by_table[i]["crane"]
            if Crane == "Crane 1":
                info_crane = info_crane_1
            if Crane == "Crane 2":
                info_crane = info_crane_2
            
            Crane_name = info_crane["name"]
            # Checking if the crane is already used by other lift point
            if Crane_name not in Data_crane.keys():
                info_crane_used={}
                info_crane_used["DDF"]=info_crane["DDF"]
                info_hoist={}
                info_hoist["Data"] = info_crane[Hoist]
                info_hoist["Points"] = [point]
                info_crane_used[Hoist] =info_hoist
                
                Data_crane.update({Crane_name:info_crane_used})

            else: 
                # Checking if the hoist is already used by other lift point
                if Hoist not in Data_crane[Crane_name].keys():
                    info_hoist={}
                    info_hoist["Data"] = info_crane[Hoist]
                    info_hoist["Points"] = [point]
                    Data_crane[Crane_name].update({Hoist:info_hoist})

                else:
                    
                    Data_crane[Crane_name][Hoist]["Points"].append(point)
            
        return Data_crane

    @ property
    def get_data_SKL(self):
        return self.data_SKl

    @ property 
    def get_n_lifts(self):
        return self.N_lifts
    @ property 
    def get_max_cog_shift(self):
        return self.COG_shift
    
    @ property 
    def get_load_dis_perc(self):
        return self.Load_dis_perc
    
    @ property 
    def get_factors(self):
        return self.factors
    
    @ property 
    def get_load_dis_t(self):
        return self.Load_dis_t
    
    @ property 
    def get_data_general(self):
        return self.data_general
    
    @ property 
    def get_data_factors(self):
        return self.data_general_factor
    
    @property
    def get_rigging_checks(self):
        return self.Rigging_checks