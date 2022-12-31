
from .calculations import Calc_COG_env, \
    Calc_load_dis,Calc_factors,Calc_rigging,Calc_SKL,\
        distance_points_3d,Calc_crane
from .Default_inputs import df_rigging

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
        skl_params= params.tab_2.section_3
        rigging_params= params.tab_3.section_1
        #other_rigging_params= params.tab_3.section_2
        crane_params = params.tab_4
        #file_params= params.tab_5



        # making tef factor (kan worden verwijdert)

        tef_factor = []
        for i in range(self.N_lifts):
            tef_factor.append(1)

        # Getting data 
        self.data_cranes = self.make_data_cranes(crane_params)
        self.data_general = self.make_data_general(general_params)

        self.data_SSF_factors = self.make_data_SSF_factor(
                                                SSF_params)
        self.data_general_factor = self.make_data_general_factor(
                                                general_factor_params)
        self.data_rigging = self.make_data_rigging(rigging_params)
        self.data_SKl = self.make_data_skl(skl_params)
        SKL_results = [skl_params["skl1"],
                       skl_params["skl2"],
                       skl_params["skl3"],
                       skl_params["skl4"]]
        #print(self.data_SKl)
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
        _Calc_rigging = Calc_rigging(self.data_rigging,
                                     _Calc_factors,
                                     _Calc_load_dis,
                                     self.data_general["LW"],
                                     SKL_results)
        _Calc_crane = Calc_crane(self.data_cranes,
                                 _Calc_factors,
                                 _Calc_load_dis,
                                 self.data_general["LW"])


        # Making attributes so it can be shared with the other method 
        self.Load_dis_perc = _Calc_load_dis.return_load_dis
        self.Load_dis_t = _Calc_load_dis.get_load_dis_tons
        self.factors = _Calc_factors.get_general_factors
        self.COG_shift = _Calc_load_dis.get_max_cog_shifts
        self.Rigging_checks = _Calc_rigging.get_rigging_calc_total
        self.Crane_checks = _Calc_crane.get_crane_results
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
            L=distance_points_3d(Hook_point,Lift_point)
            print("Sling "+str(i+1)+": "+str(L))
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

    def make_data_rigging(self, params):
        Data_rigging = []
        id_slings_list = list(df_rigging["Slings"].keys())
        id_shackles_list = list(df_rigging["Shackles"].keys())
        
        dynamic_array = params.Rigging_data
        for ans in dynamic_array:
            row = {}
            row["Name"] = ans["RiggingPoint"]
            row["Material"]= ans['rigging_material']
            row["Points"]=ans["Points"]
            row["RWP"]=ans["RWP"]
            row["Angle_1"]=ans['transvere_angle']
            row["Angle_2"]=ans['longitudinal_angle']
            row["SSF_ans"] = ans["SSF"]
            # skl array
            row["SKL"] = ["ans", 0,0]
            row["SKL"][0] = ans["SKL"]
            row["SKL"][1]= ans["SKL_value"]
            row["TRF_ans"] = ans["TRF"]
            row["SLDF_ans"] = ans["SLDF"]
            # sling is equal to a array 
            row["sling"] = ["ID","type", 0, 0, 0]
            id_sling = ans.Table_sling_grommet[0]['ID_number']
            row["sling"][0] = str(id_sling)
            if id_sling not in id_slings_list:
                # it is not in the data base 
                print("sling Is niet in data base")
                row["sling"][1] = ans.Table_sling_grommet[0]['Type']
                row["sling"][2] = ans.Table_sling_grommet[0]['SWL']
                row["sling"][3] = ans.Table_sling_grommet[0]['D']
            else:
                print("sling is in data base")
                info_sling = df_rigging["Slings"][id_sling]
                row["sling"][1] = info_sling["type"]
                row["sling"][2] = info_sling["MBL"]
                row["sling"][3] = info_sling["Dia"]
            row["sling"][4] = ans.Table_sling_grommet[0]['n_parts']

            # Connecting points upper 
            row ["Connection_upper"] = ["Type",0, 0]
            type_connec_upper = ans.Table_connecting_points[0]["connections"] 
            row ["Connection_upper"][0] = type_connec_upper
            
            if "Shackle" in type_connec_upper:
                id_shackle = type_connec_upper.split(" ",1)[1]
                if id_shackle not in id_shackles_list:
                    print("Upper Shackle not in data base")
                    row["Connection_upper"][1] = ans.Table_connecting_points[0]["dia"]
                    row["Connection_upper"][2] = ans.Table_connecting_points[0]["SWL"] 
                else: 
                    print("Upper shackle in data base")
                    info_shackle = df_rigging["Shackles"][id_shackle] 
                    if isinstance(info_shackle["D"],str) == True:
                        row ["Connection_upper"][1]=ans.Table_connecting_points[0]["dia"]
                    else:
                        row ["Connection_upper"][1] = info_shackle["D"]
                    row ["Connection_upper"][2] = info_shackle["WLL"] 
            else:
                row ["Connection_upper"][1] = ans.Table_connecting_points[0]["dia"]
                row ["Connection_upper"][2] = ans.Table_connecting_points[0]["SWL"] 

            # Connecting points lower 
            row ["Connection_lower"] = ["Type",0, 0]
            type_connec_upper = ans.Table_connecting_points[1]["connections"] 
            row ["Connection_lower"][0] = type_connec_upper

            if "Shackle" in type_connec_upper:
                id_shackle = type_connec_upper.split(" ",1)[1]
                if id_shackle not in id_shackles_list:
                    print("Lower Shackle not in data base")
                    row ["Connection_lower"][1] = ans.Table_connecting_points[1]["dia"]
                    row ["Connection_lower"][2] = ans.Table_connecting_points[1]["SWL"] 
                else: 
                    info_shackle = df_rigging["Shackles"][id_shackle] 
                    if isinstance(info_shackle["D"],str) == True:
                        row ["Connection_lower"][1]=ans.Table_connecting_points[1]["dia"]
                    else:
                        row ["Connection_lower"][1] = info_shackle["D"]
                    row ["Connection_lower"][2] = info_shackle["WLL"] 
                    print("Lower Shackle in data base")
            else:
                row ["Connection_lower"][1] = ans.Table_connecting_points[1]["dia"]
                row ["Connection_lower"][2] = ans.Table_connecting_points[1]["SWL"] 
            Data_rigging.append(row)
        return Data_rigging

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

    @property 
    def get_crane_checks(self):
        return self.Crane_checks