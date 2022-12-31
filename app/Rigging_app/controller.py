from viktor import ViktorController
from viktor.result import SetParamsResult
from viktor.views import  PlotlyView, PlotlyResult, DataGroup, \
    DataItem, DataResult, DataView,PlotlyAndDataView,SVGView, \
        SVGAndDataView,SVGAndDataResult,SVGResult,Label,GeometryAndDataView,\
            GeometryAndDataResult,PlotlyAndDataResult
from .calculations import Calc_SKL
import numpy as np
from .model import communicater_calculations
from .parametrization import Parametrization
from plotly.subplots import make_subplots
import plotly.graph_objects as go

class Main_Controller(ViktorController):
    label = 'Rigging Checks'
    parametrization = Parametrization
    def skew_load_factor(self,params,**kwargs):
        data = communicater_calculations(params)

        Data_skl = data.get_data_SKL
        Data_general = data.get_data_general

        result= Calc_SKL(Data_skl,Data_general)
        max_skew_load_factor=result.get_max_skew_load_factor
        pitch_roll_angles=result.get_max_min_pitch_roll_angles
        
        return SetParamsResult({"tab_2":{
                                    "section_3":{
                                        "skl1":round(max_skew_load_factor[0],2),
                                        "skl2":round(max_skew_load_factor[1],2),
                                        "skl3":round(max_skew_load_factor[2],2),
                                        "skl4":round(max_skew_load_factor[3],2),
                                        "min_pitch":round(pitch_roll_angles["Min pitch"],2),
                                        "max_pitch":round(pitch_roll_angles["Max pitch"],2),
                                        "min_roll":round(pitch_roll_angles["Min roll"],2),
                                        "max_roll":round(pitch_roll_angles["Max roll"],2)

                                     

                                    }  

        }})
    @PlotlyView("OUTPUT",duration_guess=1)
    def data(self,params,**kwargs):

        data = communicater_calculations(params)
        # gettin data
        max_cog_shift = np.round(data.get_max_cog_shift,3)
        load_dis_perc = data.get_load_dis_perc
        load_dis_t = data.get_load_dis_t
        factors = data.get_factors
        N_lifts = data.get_n_lifts
        data_factors = data.get_data_factors
        point_names = ["A","B","C","D"]
        TEF_angles = data.get_angles
        # making figure 
        fig = make_subplots(
            rows=3, cols=1,
            vertical_spacing=0.03,
            specs=[[{"type": "table"}],
                    [{"type": "table"}],
                    [{"type": "table"}]]
            )
        df_table_1= [point_names[:N_lifts],
                     load_dis_perc,
                     load_dis_t,
                     max_cog_shift]

        df_table_2 = [[],[],[]]
        n_ssf_factors = sum('SSF' in s for s in list(factors.keys())) 
        print(n_ssf_factors)
        for key, values in data_factors.items():
            if key!="COG_envelope" and key!="TEF":
                df_table_2[0].append(key)
                df_table_2[1].append(values)
                df_table_2[2].append(factors[key])
        for i in range(n_ssf_factors):
            i +=1
            df_table_2[0].append("SSF"+str(i))
            df_table_2[1].append("Sling safety factor")
            df_table_2[2].append(factors["SSF"+str(i)])
        df_table_2[0].append("COG")
        df_table_2[1].append(data_factors["COG_envelope"])
        df_table_2[2].append("see table below")
        df_table_2[0].append("TEF")
        df_table_2[1].append(TEF_angles)
        df_table_2[2].append("See table below")
        df_table_3= [point_names[:N_lifts],
                     factors["COG_envelope"],
                     np.around(factors["TEF"],3)]

        fig.add_trace(
            go.Table(
                header=dict(
                    values=["Point","Load dis[%]","Load dis[t]","Max cog shift[-]"],
                    font=dict(size=15),
                    align="left"
                ),
                cells=dict(
                    values=df_table_1,
                    align = "left",
                    ),
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Table(
                header=dict(
                    values=["What","Answer","Factor[-]"],
                    font=dict(size=15),
                    align="left"
                ),
                cells=dict(
                    values=df_table_2,
                    align = "left",
                    ),
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=["point","COG shift factor rigging","TEF factor"],
                    font=dict(size=15),
                    align="left"
                ),
                cells=dict(
                    values=df_table_3,
                    align = "left")
            ),
            row=3, col=1
        )
        
        return PlotlyResult(fig.to_json())        

    @DataView("Rigging output",duration_guess=1)
    def data_rigging(self,params,**kwargs):

        data = communicater_calculations(params)
       
        Riggin_checks=data.get_rigging_checks
        Rigging_other_checks=data.get_rigging_checks_other
        print(Rigging_other_checks)
        #print(Riggin_results_total)
        
        data_group_equipment=[]
        for name,results in Rigging_other_checks.items():
            group=DataItem(name," ",subgroup=DataGroup(
                        DataItem("Type",results["Type"],explanation_label="Type of equipment:"),
                        DataItem("id_number",results["id_number"],explanation_label="Id number:"),
                        DataItem("Weight",results["Weight"],prefix='[kg]',explanation_label="Weight of object"),
                        DataItem("WLL",results["WLL"],prefix='[t]',explanation_label="Working load limit"),
                        DataItem("COG",round(results["COG"],2),prefix='[-]',explanation_label="COG shift factor"),
                        DataItem("TEF",round(results["TEF"],2),prefix='[-]',explanation_label="Tilt effect factor"),
                        DataItem("SKL",round(results["SKL"][2],2),prefix='[-]',explanation_label="Skew load factor"),
                        DataItem("Perc",round(results["Perc"]*100,2),prefix='[%]',explanation_label="Percentage of load"),
                        DataItem("MDRL",round(results["MDRL"],2),prefix='[t]',explanation_label="Maximum dynamic rigging load"),
                        DataItem("Unity check",round(results["Uc"],2),prefix='[-]',explanation_label="DHL/WLL"),))
            data_group_equipment.append(group)
        
        data_group_total=[]
        for rigging_point,results in Riggin_checks.items():
            group=DataItem(rigging_point," ",subgroup=DataGroup(
                        DataItem("Type",results["sling"][1],prefix='[-]',explanation_label="Type of sling/grommet"),
                        DataItem("D",results["sling"][3],prefix='[mm]',explanation_label="Diameter sling/grommet"),
                        DataItem("SWL",round(results["sling"][2],0),prefix='[t]',explanation_label="SWL sling/grommet"),                   
                        DataItem("TEF",round(results["TEF"],2),prefix='[-]',explanation_label="Tilt effect factor"),
                        DataItem("FDRL",round(results["FDRL"],2),prefix='[t]',explanation_label="Factored Dynamic Rigging Load(LW * WCF * DAF * YAW * TEF)"),
                        DataItem("Perc",round(results["perc"]*100,2),prefix='[%]',explanation_label="Load perc on lifting point"),
                        DataItem("COG",round(results["COG"],2),prefix='[-]',explanation_label="COG shift factor"),
                        DataItem("SKL",round(results["SKL"][2],2),prefix='[-]',explanation_label="skew load factor"),
                        DataItem("VLLP",round(results["VLLP"],2),prefix='[t]',explanation_label="Vertical load to lifting point (Perc * FDRL * COG shift factor * SKL)"),
                        DataItem("RWP",results["RWP"],prefix='[t]',explanation_label="Rigging weight above lifting point"),
                        DataItem("VLUS",round(results["VLUS"],2),prefix='[t]',explanation_label="Vertical load on slings (VLLP + (RWP * DAF * WCF)):"),
                        DataItem("Angle 1",results["Angle_1"],prefix='[deg]',explanation_label="Sling angle with vertical, transverse:"),
                        DataItem("Angle 2",results["Angle_2"],prefix='[deg]',explanation_label="Sling angle with vertical, longitudinal:"),
                        DataItem("IFUS",round(results["IFUS"],2),prefix='[t]',explanation_label="inline force slings"),
                        DataItem("n",results["sling"][4],prefix='[-]',explanation_label="Amount of parts"),
                        DataItem("SLDF distribution",results["SLDF_dis"],prefix="[-]",explanation_label="SLing load distributie"),
                        DataItem("SLDF",round(results["SLDF"],2),prefix='[-]',explanation_label="Sling load distributie factor"),
                        DataItem("IFUP",round(results["IFUP"],2),prefix='[t]',explanation_label="Inline force one part(IFUS/n)*SLDF"),
                        DataItem("TRF",round(results["TRF"],2),prefix='[-]',explanation_label="Termination factor"),
                        DataItem("Bending d",results["min_d"],prefix='[mm]',explanation_label="Minimum diameter over wich sling body is bent"),
                        DataItem("BRF",round(results["BRF"],2),prefix='[-]',explanation_label="bending reduction factor"),
                        DataItem("Reduction factor",results["Red_factor"],prefix='[-]',explanation_label="Max BRF/TRF"),
                        DataItem("SSF",results["SSF"],prefix='[-]',explanation_label="Sling safety factor"),
                        DataItem("Req swl",round(results["sling"][-2],2),prefix='[t]',explanation_label="Required SWL sling/grommet(IFUP*SSF*red factor)"),
                        DataItem("UC sling/grommet",round(results["sling"][-1],2),prefix='[-]',explanation_label="Unity check sling/grommet"),
                        DataItem("UC upper shackle",results["Connection_upper"][-1],prefix='[-]',explanation_label="Unity check upper shackle"),
                        DataItem("UC lower shackle",results["Connection_lower"][-1],prefix='[-]',explanation_label="Unity check lower shackle")))
            data_group_total.append(group)  

        data_visualize=DataGroup(DataItem("Results rigging calc"," ",subgroup=DataGroup(*data_group_total)),
                                            DataItem("Results equipment"," ",subgroup=DataGroup(*data_group_equipment)))
        return DataResult(data_visualize)


    @DataView("Crane ouput", duration_guess=1)
    def crane_data(self,params,**kwargs):
        
        data = communicater_calculations(params)
       
        Crane_checks=data.get_crane_checks
    
        print(Crane_checks)
        names=list(Crane_checks.keys())
        print(names)
        data_group_crane_1_hoist=[]
        data_total=[]

        for info, values in Crane_checks[names[0]].items():
            
            if info  != "DDF":
                group=DataItem("Checks " +info," ",subgroup=DataGroup(
                        DataItem("Points",values["Points"],prefix='[-]',explanation_label="Which points is it connected to"),
                        DataItem("Percentage",round(values["perc"],2),prefix='[%]',explanation_label="Percentage vertical load"),
                        DataItem("TEF",round(values["TEF"],2),prefix='[-]',explanation_label="Tilt effect factor"),
                        DataItem("Offlead",round(values["Offlead"],2),prefix='[deg]',explanation_label="Angle with vertical, in line with boom(offlead)"),
                        DataItem("CAP",values["CAP"],prefix='[t]',explanation_label="Capacity hoist"),
                        DataItem("HLV",round(values["HLV"],2),prefix='[t]',explanation_label="Vertical hook load"),
                        DataItem("HL",round(values["HL"],2),prefix='[t]',explanation_label="Hook load hoist HLV/cos(offlead)"),
                        DataItem("UC",round(values["UC"],2),prefix='[-]',explanation_label="Unity check"),
                        ))
                data_group_crane_1_hoist.append(group)
            else:
                DDF_crane1=values
        data_group_crane_2_hoist=[]
        if len(names)==2:
            
            for info, values in Crane_checks[names[1]].items():
                
                if info  != "DDF":
                    group=DataItem("Checks " +info," ",subgroup=DataGroup(
                            DataItem("Points",values["Points"],prefix='[-]',explanation_label="Which points is it connected to"),
                            DataItem("Percentage",round(values["perc"],2),prefix='[%]',explanation_label="Percentage vertical load"),
                            DataItem("TEF",round(values["TEF"],2),prefix='[-]',explanation_label="Tilt effect factor"),
                            DataItem("Offlead",round(values["Offlead"],2),prefix='[deg]',explanation_label="Angle with vertical, in line with boom(offlead)"),
                            DataItem("CAP",values["CAP"],prefix='[t]',explanation_label="Capacity hoist"),
                            DataItem("HLV",round(values["HLV"],2),prefix='[t]',explanation_label="Vertical hook load"),
                            DataItem("HL",round(values["HL"],2),prefix='[t]',explanation_label="Hook load hoist HLV/cos(offlead)"),
                            DataItem("UC",round(values["UC"],2),prefix='[-]',explanation_label="Unity check"),
                            ))
                    data_group_crane_2_hoist.append(group)
                else:
                    DDF_crane2=values
        else:
            DDF_crane2=1
            names.append("Not used")

                
        groub_crane1=DataGroup(DataItem("Checks: "+names[0],"DDF:"+str(DDF_crane1),subgroup=DataGroup(*data_group_crane_1_hoist)),
                                DataItem("Checks: "+names[1],"DDF:"+str(DDF_crane2),subgroup=DataGroup(*data_group_crane_2_hoist)))


            





        return DataResult(groub_crane1)